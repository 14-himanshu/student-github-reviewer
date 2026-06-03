import os
import time
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .state import ReviewState

load_dotenv()

# Set up the Groq AI brain using Llama 3.1
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)


def extract_github_data(state: ReviewState):
    username = state["username"]
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
    try:
        user_url = f"https://api.github.com/users/{username}"
        user_resp = requests.get(user_url, headers=headers)
        repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5"
        repos_resp = requests.get(repos_url, headers=headers)
        if user_resp.status_code == 200 and repos_resp.status_code == 200:
            user_data = user_resp.json()
            repos_data = repos_resp.json()
            repo_names = [repo["name"] for repo in repos_data]
            languages = list(set([repo["language"] for repo in repos_data if repo["language"]]))
            
            # Fetch README for top 2 repos
            readmes = {}
            for repo_name in repo_names[:2]:
                readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
                readme_headers = headers.copy()
                readme_headers["Accept"] = "application/vnd.github.v3.raw"
                readme_resp = requests.get(readme_url, headers=readme_headers)
                if readme_resp.status_code == 200:
                    readmes[repo_name] = readme_resp.text[:300] + "..."

            real_data = {
                "avatar_url": user_data.get("avatar_url", ""),
                "followers": user_data.get("followers", 0),
                "recent_repos": repo_names,
                "primary_languages": languages,
                "public_repos_count": user_data.get("public_repos", 0),
                "repo_readmes": readmes
            }
            return {"github_data": real_data}
        else:
            return {"github_data": {"error": f"API Error: User {username} not found."}}
    except Exception as e:
        return {"github_data": {"error": str(e)}}


def _invoke_llm_with_retry(messages, max_retries: int = 5, base_delay: float = 5.0):
    """Invoke the LLM with exponential backoff retry on rate limit (429) errors."""
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = "429" in str(e) or "rate limit" in error_str or "rate_limit" in error_str
            if is_rate_limit and attempt < max_retries - 1:
                wait = base_delay * (2 ** attempt)
                time.sleep(wait)
            else:
                raise


def code_mentor_review(state: ReviewState):
    username = state["username"]
    data = state["github_data"]
    prompt = f"""
    You are an encouraging Code Mentor. Review this GitHub portfolio data for '{username}'.
    Data: {data}
    
    CRITICAL: You MUST begin your response with exactly these two lines:
    [GRADE: <letter grade from A+ to C>]
    [BADGES: <comma separated list of 2-3 short badges like 'TypeScript Pro', 'Open Source Contributor'>]
    
    After those two lines, write a short, professional review. Highlight their strengths based on their languages, follower count,
    and comment on the quality of their recently updated READMEs (provided in the data).
    Suggest 1 or 2 actionable improvements.
    """
    try:
        response = _invoke_llm_with_retry([HumanMessage(content=prompt)])
        return {"feedback": response.content}
    except Exception as e:
        error_str = str(e).lower()
        is_rate_limit = "429" in str(e) or "rate limit" in error_str or "rate_limit" in error_str
        if is_rate_limit:
            fallback_msg = (
                "[GRADE: B+]\n"
                "[BADGES: Rising Star, Consistent Builder]\n\n"
                "**AI Mentor:**\n\n"
                "The AI service is currently experiencing high demand and couldn't generate a personalized review right now. "
                "However, having a GitHub portfolio is a great start! Keep building projects, exploring the languages in your repositories, "
                "and remember to add clear documentation (READMEs) and tests to make your repositories stand out. Keep up the great work!"
            )
            return {"feedback": fallback_msg}
        raise