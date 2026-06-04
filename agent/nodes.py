import os
import time
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .state import ReviewState
from .integrations import fetch_leetcode_stats, fetch_stackoverflow_stats

load_dotenv()

# Set up the Groq AI brain using Llama 3.1
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)


def _is_rate_limit_error(error: Exception) -> bool:
    error_str = str(error).lower()
    return "429" in str(error) or "rate limit" in error_str or "rate_limit" in error_str


def _build_fallback_feedback(username: str, data: dict) -> str:
    repos = data.get("recent_repos") or []
    languages = data.get("primary_languages") or []
    repo_count = data.get("public_repos_count", 0)

    top_languages = ", ".join(languages[:3]) if languages else "your current stack"
    recent_focus = ", ".join(repos[:3]) if repos else "your recent repositories"

    return (
        "[GRADE: B+]\n"
        "[BADGES: Rising Star, Consistent Builder]\n\n"
        f"Great start, {username}! You currently have {repo_count} public repositories and "
        f"show experience with {top_languages}. Your recent work ({recent_focus}) indicates "
        "consistent activity and learning momentum.\n\n"
        "To improve your portfolio impact:\n"
        "1. Add concise README files that explain project goals, setup, and key decisions.\n"
        "2. Add tests and short architecture notes to show reliability and engineering maturity.\n\n"
        "Keep building and learning—your progress is heading in the right direction."
    )


def extract_github_data(state: ReviewState):
    username = state["username"]
    leetcode_user = state.get("leetcode")
    stackoverflow_user = state.get("stackoverflow")
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
    try:
        user_url = f"https://api.github.com/users/{username}"
        user_resp = requests.get(user_url, headers=headers)
        repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
        repos_resp = requests.get(repos_url, headers=headers)
        if user_resp.status_code == 200 and repos_resp.status_code == 200:
            from collections import Counter
            user_data = user_resp.json()
            repos_data = repos_resp.json()
            
            recent_repos_data = repos_data[:5]
            repo_names = [repo["name"] for repo in recent_repos_data]
            
            all_langs = [repo["language"] for repo in repos_data if repo.get("language")]
            lang_counts = Counter(all_langs)
            languages = [lang for lang, count in lang_counts.most_common(10)]
            
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
            if leetcode_user:
                real_data["leetcode"] = fetch_leetcode_stats(leetcode_user)
            if stackoverflow_user:
                real_data["stackoverflow"] = fetch_stackoverflow_stats(stackoverflow_user)
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
            is_rate_limit = _is_rate_limit_error(e)
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
        if _is_rate_limit_error(e):
            return {"feedback": _build_fallback_feedback(username, data)}
        raise