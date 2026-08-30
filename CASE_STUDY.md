# Case Study: DevScope

**DevScope is an AI-powered app that analyzes a GitHub user's profile and repositories, then returns mentorship-style feedback on their portfolio.**

**Technologies:** Streamlit, FastAPI, LangGraph, Groq

---

## Project Summary

DevScope analyzes a GitHub profile and repository set, then converts that information into practical, mentorship-style feedback. 
The app is designed to help students understand how their public work looks to a reviewer and what they can improve next.

## What You Used

This stack intentionally keeps the UI simple while letting the AI pipeline do the heavy lifting.

*   **Frontend:** Streamlit
*   **Backend/API:** FastAPI (Python) with Uvicorn.
*   **AI / Orchestration:** LangGraph and LangChain.
*   **LLM:** Groq running llama-3.1-8b-instant.
*   **Data and API Integration:** GitHub REST API endpoints for user and repository data.
*   **Other libraries:** requests and python-dotenv.

## Hosting / Deployment

The app is deployed as two separate services so the UI and API can scale and fail independently.

*   **Platform:** Render.
*   **Deployment model:** one backend API service and one frontend Streamlit service.
*   **Configuration:** `render.yaml` with GROQ_API_KEY, GITHUB_TOKEN, and BACKEND_URL environment variables.

## Core Features

The product is focused on fast feedback and a clear review experience.

*   Enter a GitHub username and analyze the portfolio.
*   Fetch recent repositories, languages, and public repository count.
*   Generate AI feedback with actionable suggestions.
*   Handle API and LLM issues with timeouts, rate limits, and retries.
*   Present a clean UI with metrics and expandable review sections.

## Architecture

The high-level flow is simple: collect, enrich, review, and render.

1.  The user submits a GitHub username in the Streamlit UI.
2.  The UI calls a FastAPI POST `/review` endpoint.
3.  A LangGraph pipeline runs `extract_github_data` against the GitHub API, then `code_mentor_review` through the Groq LLM.
4.  The backend returns JSON containing extracted data and mentor feedback.
5.  The UI renders metrics and the mentor review response.

## Portfolio-ready Blurb

Built a full-stack AI portfolio reviewer using Streamlit, FastAPI, LangGraph, and Groq Llama 3.1. The app consumes the GitHub REST API to extract repository and language insights, then generates mentorship-style feedback through an LLM pipeline. Deployed as separate frontend and backend services on Render, with production-style handling for rate limits, timeouts, and API errors.
