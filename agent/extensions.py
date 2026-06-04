from langchain_core.messages import HumanMessage
from agent.nodes import _invoke_llm_with_retry

def generate_roadmap_and_gaps(username: str, github_data: dict) -> str:
    prompt = f"""
    You are an expert career coach and senior engineer. Analyze this GitHub portfolio data for '{username}':
    {github_data}
    
    Identify 1-2 major skill gaps based on the languages and repositories they have. 
    Then provide a concise, actionable 3-step learning roadmap to help them become a more well-rounded developer.
    Format your response in Markdown with clear headings.
    """
    response = _invoke_llm_with_retry([HumanMessage(content=prompt)])
    return response.content

def generate_project_ideas(username: str, github_data: dict) -> str:
    prompt = f"""
    You are a creative technical mentor. Based on this GitHub portfolio data for '{username}':
    {github_data}
    
    Suggest 3 specific, portfolio-worthy project ideas that would complement their existing skills.
    For each idea, briefly explain WHY it's a good fit for them and what technologies they should use.
    Format your response in Markdown using bullet points or numbered lists.
    """
    response = _invoke_llm_with_retry([HumanMessage(content=prompt)])
    return response.content

def generate_interview_questions(username: str, github_data: dict) -> str:
    prompt = f"""
    You are a technical interviewer at a top tech company. Based on the primary languages and repositories in this GitHub portfolio data for '{username}':
    {github_data}
    
    Generate 5 tailored mock interview questions (a mix of technical and architectural).
    Provide brief hints or the key concepts they should mention for each question.
    Format your response in Markdown.
    """
    response = _invoke_llm_with_retry([HumanMessage(content=prompt)])
    return response.content

def generate_repo_deep_dive(username: str, repo_name: str, repo_data: dict) -> str:
    prompt = f"""
    You are an expert code reviewer. Perform a deep dive analysis on this specific repository '{repo_name}' for the user '{username}'.
    Repository Data (including README, basic info, etc.):
    {repo_data}
    
    Provide a detailed review of this repository. Include:
    - Overall impression and purpose of the repository.
    - Strengths in their setup or documentation.
    - 2 specific recommendations for improving this repository to make it production-ready.
    Format your response in Markdown with clear headings.
    """
    response = _invoke_llm_with_retry([HumanMessage(content=prompt)])
    return response.content
