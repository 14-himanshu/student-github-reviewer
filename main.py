import datetime
import logging
import os
import requests
from fastapi import FastAPI, HTTPException, Response, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from agent.graph import github_reviewer_app
from agent.nodes import _invoke_llm_with_retry, llm
from agent.extensions import generate_roadmap_and_gaps, generate_project_ideas, generate_interview_questions, generate_repo_deep_dive
from backend.pdf_generator import create_resume_pdf
from backend.database import get_db, engine
import backend.models as models
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel
from typing import List

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevScope — AI GitHub Portfolio Reviewer",
    description="AI-powered GitHub portfolio analysis and mentorship feedback.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="frontend"), name="assets")

CACHE_TTL = 24 * 60 * 60  # 24 hours

def get_cached_data(username: str, db: Session):
    entry = db.query(models.CacheEntry).filter(models.CacheEntry.username == username).first()
    if entry:
        if (datetime.datetime.utcnow() - entry.timestamp).total_seconds() < CACHE_TTL:
            return entry.data
    return None

def set_cached_data(username: str, data: dict, db: Session):
    entry = db.query(models.CacheEntry).filter(models.CacheEntry.username == username).first()
    if entry:
        entry.data = data
        entry.timestamp = datetime.datetime.utcnow()
    else:
        entry = models.CacheEntry(username=username, data=data, timestamp=datetime.datetime.utcnow())
        db.add(entry)
    db.commit()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_str = str(exc)
    logger.error(f"Unhandled exception: {error_str}", exc_info=True)
    if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
        return JSONResponse(
            status_code=429,
            content={"detail": "Groq API rate limit exceeded. Please wait a moment and try again."},
        )
    return JSONResponse(status_code=500, content={"detail": f"An internal error occurred: {error_str}"})


@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.post("/review")
def review_portfolio(username: str, leetcode: str = None, stackoverflow: str = None, db: Session = Depends(get_db)):
    cached_data = get_cached_data(username, db)
    if cached_data:
        logger.info(f"Returning cached data for {username}")
        return cached_data

    initial_state = {"username": username, "leetcode": leetcode, "stackoverflow": stackoverflow}
    
    logger.info(f"Running agent graph for {username}")
    result = github_reviewer_app.invoke(initial_state)

    result_data = {
        "username": result["username"],
        "extracted_data": result.get("github_data"),
        "mentor_feedback": result.get("feedback"),
    }
    
    set_cached_data(username, result_data, db)
    return result_data

@app.post("/cover-letter")
def generate_cover_letter(username: str, db: Session = Depends(get_db)):
    cached_data = get_cached_data(username, db)
    if not cached_data:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    github_data = cached_data.get("extracted_data")
    prompt = f"""
    You are an expert career coach. Write a highly professional, 3-paragraph cover letter for a Software Engineering role for '{username}'.
    Base the cover letter strictly on this GitHub portfolio data:
    {github_data}
    
    Do not use placeholders for the recipient or company name (just use 'Hiring Manager' and 'your company'). 
    Emphasize their top languages and specific repositories. Write directly from the perspective of the applicant.
    """
    
    response = _invoke_llm_with_retry([HumanMessage(content=prompt)])
    return {"cover_letter": response.content}

@app.post("/roadmap")
def get_roadmap(username: str, db: Session = Depends(get_db)):
    cached_data = get_cached_data(username, db)
    if not cached_data:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    content = generate_roadmap_and_gaps(username, cached_data.get("extracted_data"))
    return {"roadmap": content}

@app.post("/project-ideas")
def get_project_ideas(username: str, db: Session = Depends(get_db)):
    cached_data = get_cached_data(username, db)
    if not cached_data:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    content = generate_project_ideas(username, cached_data.get("extracted_data"))
    return {"ideas": content}

@app.post("/interview-prep")
def get_interview_prep(username: str, db: Session = Depends(get_db)):
    cached_data = get_cached_data(username, db)
    if not cached_data:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    content = generate_interview_questions(username, cached_data.get("extracted_data"))
    return {"questions": content}

@app.post("/generate-pdf")
def generate_pdf(username: str, db: Session = Depends(get_db)):
    cached_data = get_cached_data(username, db)
    if not cached_data:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    feedback = cached_data.get("mentor_feedback", "")
    pdf_bytes = create_resume_pdf(username, feedback)
    return Response(content=pdf_bytes, media_type="application/pdf")

@app.post("/repo-deep-dive")
def repo_deep_dive(username: str, repo_name: str):
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
    
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    repo_resp = requests.get(repo_url, headers=headers)
    if repo_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Repository not found on GitHub.")
    
    repo_info = repo_resp.json()
    
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    readme_headers = headers.copy()
    readme_headers["Accept"] = "application/vnd.github.v3.raw"
    readme_resp = requests.get(readme_url, headers=readme_headers)
    readme_text = readme_resp.text[:1500] if readme_resp.status_code == 200 else "No README available."
    
    repo_data = {
        "description": repo_info.get("description"),
        "language": repo_info.get("language"),
        "stars": repo_info.get("stargazers_count"),
        "open_issues": repo_info.get("open_issues_count"),
        "readme_snippet": readme_text
    }
    
    content = generate_repo_deep_dive(username, repo_name, repo_data)
    return {"deep_dive": content}

@app.post("/reviews/save")
def save_review(username: str, db: Session = Depends(get_db)):
    cached_data = get_cached_data(username, db)
    if not cached_data:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    new_review = models.Review(
        username=username,
        github_data=cached_data.get("extracted_data"),
        feedback_markdown=cached_data.get("mentor_feedback")
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return {"review_id": new_review.id}

@app.get("/reviews/{review_id}")
def get_review(review_id: str, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    return {
        "username": review.username,
        "extracted_data": review.github_data,
        "mentor_feedback": review.feedback_markdown,
        "created_at": review.created_at
    }

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    username: str
    messages: List[ChatMessage]

@app.post("/chat")
def chat_with_mentor(request: ChatRequest, db: Session = Depends(get_db)):
    cached_data = get_cached_data(request.username, db)
    if not cached_data:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    github_data = cached_data.get("extracted_data")
    
    system_prompt = f"You are a helpful AI Code Mentor. You are currently mentoring {request.username}. Here is their portfolio data: {github_data}. Answer their questions concisely and supportively."
    
    langchain_msgs = [SystemMessage(content=system_prompt)]
    for m in request.messages:
        if m.role == "user":
            langchain_msgs.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            langchain_msgs.append(AIMessage(content=m.content))
            
    response = llm.invoke(langchain_msgs)
    return {"response": response.content}