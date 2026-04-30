"""
Student GitHub Reviewer — FastAPI Backend

An AI-powered tool that analyzes a student's GitHub portfolio
and provides mentorship feedback using LangGraph + Groq (Llama 3.1).
"""

from fastapi import FastAPI, HTTPException
from agent.graph import github_reviewer_app

app = FastAPI(
    title="Student GitHub Reviewer",
    description="AI-powered GitHub portfolio analysis and mentorship feedback.",
    version="1.0.0",
)


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
    return {
        "username": result["username"],
        "extracted_data": result.get("github_data"),
        "mentor_feedback": result.get("feedback"),
    }