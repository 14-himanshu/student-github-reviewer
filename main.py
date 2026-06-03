"""
Student GitHub Reviewer — FastAPI Backend

An AI-powered tool that analyzes a student's GitHub portfolio
and provides mentorship feedback using LangGraph + Groq (Llama 3.1).
"""

import time
from fastapi import FastAPI, HTTPException
from agent.graph import github_reviewer_app

app = FastAPI(
    title="Student GitHub Reviewer",
    description="AI-powered GitHub portfolio analysis and mentorship feedback.",
    version="1.0.0",
)

# In-memory cache to save API calls
cache = {}
CACHE_TTL = 24 * 60 * 60  # 24 hours

@app.get("/")
def home():
    """Health-check endpoint."""
    return {"message": "GitHub Reviewer backend is running perfectly!"}


@app.post("/review")
def review_portfolio(username: str):
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
    initial_state = {"username": username}

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