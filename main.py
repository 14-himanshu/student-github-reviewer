"""
Student GitHub Reviewer — FastAPI Backend

An AI-powered tool that analyzes a student's GitHub portfolio
and provides mentorship feedback using LangGraph + Groq (Llama 3.1).
"""

import time
import os
from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from agent.graph import github_reviewer_app

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

# In-memory cache to save API calls
cache = {}
CACHE_TTL = 24 * 60 * 60  # 24 hours

# Serve frontend assets
app.mount("/assets", StaticFiles(directory="frontend"), name="assets")

@app.get("/")
def home():
    """Serve the frontend."""
    return FileResponse("frontend/index.html")


@app.post("/review")
def review_portfolio(username: str, leetcode: str = None, stackoverflow: str = None):
    """
    Analyze a GitHub user's portfolio and return AI mentor feedback.

    Args:
        username: GitHub username to review.
    """
    current_time = time.time()
    if username in cache:
        cached_data, timestamp = cache[username]
        if current_time - timestamp < CACHE_TTL:
            return cached_data

    # 1. Create the starting state for the agent graph
    initial_state = {"username": username, "leetcode": leetcode, "stackoverflow": stackoverflow}

    # 2. Run the LangGraph pipeline
    try:
        result = github_reviewer_app.invoke(initial_state)
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
            raise HTTPException(
                status_code=429,
                detail="Groq API rate limit exceeded. Please wait a moment and try again.",
            )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {error_str}")

    # 3. Return the AI's analysis
    result_data = {
        "username": result["username"],
        "extracted_data": result.get("github_data"),
        "mentor_feedback": result.get("feedback"),
    }
    
    # Save to cache
    cache[username] = (result_data, current_time)
    return result_data


from langchain_core.messages import HumanMessage
from agent.nodes import _invoke_llm_with_retry

@app.post("/cover-letter")
def generate_cover_letter(username: str):
    """
    Generate a professional cover letter based on cached GitHub data.
    """
    if username not in cache:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    cached_data, _ = cache[username]
    github_data = cached_data.get("extracted_data")
    
    prompt = f"""
    You are an expert career coach. Write a highly professional, 3-paragraph cover letter for a Software Engineering role for '{username}'.
    Base the cover letter strictly on this GitHub portfolio data:
    {github_data}
    
    Do not use placeholders for the recipient or company name (just use 'Hiring Manager' and 'your company'). 
    Emphasize their top languages and specific repositories. Write directly from the perspective of the applicant.
    """
    
    try:
        response = _invoke_llm_with_retry([HumanMessage(content=prompt)])
        return {"cover_letter": response.content}
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
            raise HTTPException(
                status_code=429,
                detail="Groq API rate limit exceeded. Please wait a moment and try again.",
            )
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_str}")

from agent.extensions import generate_roadmap_and_gaps, generate_project_ideas, generate_interview_questions

@app.post("/roadmap")
def get_roadmap(username: str):
    if username not in cache:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    cached_data, _ = cache[username]
    try:
        content = generate_roadmap_and_gaps(username, cached_data.get("extracted_data"))
        return {"roadmap": content}
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
            raise HTTPException(status_code=429, detail="Groq API rate limit exceeded. Please wait a moment and try again.")
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_str}")

@app.post("/project-ideas")
def get_project_ideas(username: str):
    if username not in cache:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    cached_data, _ = cache[username]
    try:
        content = generate_project_ideas(username, cached_data.get("extracted_data"))
        return {"ideas": content}
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
            raise HTTPException(status_code=429, detail="Groq API rate limit exceeded. Please wait a moment and try again.")
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_str}")

@app.post("/interview-prep")
def get_interview_prep(username: str):
    if username not in cache:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    cached_data, _ = cache[username]
    try:
        content = generate_interview_questions(username, cached_data.get("extracted_data"))
        return {"questions": content}
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
            raise HTTPException(status_code=429, detail="Groq API rate limit exceeded. Please wait a moment and try again.")
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_str}")

from backend.pdf_generator import create_resume_pdf

@app.post("/generate-pdf")
def generate_pdf(username: str):
    if username not in cache:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    cached_data, _ = cache[username]
    feedback = cached_data.get("mentor_feedback", "")
    
    try:
        pdf_bytes = create_resume_pdf(username, feedback)
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

import os
import requests
from agent.extensions import generate_repo_deep_dive

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
    
    try:
        content = generate_repo_deep_dive(username, repo_name, repo_data)
        return {"deep_dive": content}
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
            raise HTTPException(status_code=429, detail="Groq API rate limit exceeded.")
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_str}")

from sqlalchemy.orm import Session
from backend.database import get_db, engine
import backend.models as models

models.Base.metadata.create_all(bind=engine)

@app.post("/reviews/save")
def save_review(username: str, db: Session = Depends(get_db)):
    if username not in cache:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    cached_data, _ = cache[username]
    
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

from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    username: str
    messages: List[ChatMessage]

@app.post("/chat")
def chat_with_mentor(request: ChatRequest):
    if request.username not in cache:
        raise HTTPException(status_code=400, detail="User data not found in cache. Please run an analysis first.")
    
    cached_data, _ = cache[request.username]
    github_data = cached_data.get("extracted_data")
    
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from agent.nodes import llm
    
    system_prompt = f"You are a helpful AI Code Mentor. You are currently mentoring {request.username}. Here is their portfolio data: {github_data}. Answer their questions concisely and supportively."
    
    langchain_msgs = [SystemMessage(content=system_prompt)]
    for m in request.messages:
        if m.role == "user":
            langchain_msgs.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            langchain_msgs.append(AIMessage(content=m.content))
            
    try:
        response = llm.invoke(langchain_msgs)
        return {"response": response.content}
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "rate_limit" in error_str.lower():
            raise HTTPException(status_code=429, detail="Groq API rate limit exceeded.")
        raise HTTPException(status_code=500, detail=f"Chat failed: {error_str}")