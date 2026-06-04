# Student GitHub Reviewer

An AI-powered tool that analyzes a student's GitHub portfolio and delivers personalized mentorship feedback.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-blue)](https://github-reviewer-ui-p5e6.onrender.com)
[![Backend API](https://img.shields.io/badge/Backend%20API-Render-green)](https://student-github-reviewer-yraz.onrender.com/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This project uses a multi-step AI agent pipeline to fetch a user's GitHub profile and repositories, then generates a professional code review with actionable suggestions — powered by Groq's Llama 3.1 model.

**Live Application:** https://github-reviewer-ui-p5e6.onrender.com

---

## Features

- **AI Code Mentor Review:** Generates a professional code review using Groq's Llama 3.1 based on a user's repositories, languages, and READMEs.
- **Gamification (Grades and Badges):** The AI automatically awards an overall letter grade and custom achievement badges based on the user's GitHub activity.
- **AI Cover Letter Generator:** Instantly generate a highly professional, 3-paragraph cover letter tailored to a Software Engineering role using the user's specific GitHub portfolio data.
- **In-Memory Caching:** Subsequent requests for the same GitHub user within 24 hours load instantly, heavily reducing API rate limits.
- **Robust Rate Limit Handling:** Implements exponential backoff retries and elegant fallback feedback for handling 429 Rate Limit errors gracefully.

---

## Architecture

```
User Request
    |
    v
FastAPI Server  (POST /review?username=...)
    |
    v
LangGraph Pipeline
    |
    +-- Step 1: extract_github_data  -->  GitHub API
    |
    +-- Step 2: code_mentor_review   -->  Groq / Llama 3.1
    |
    v
JSON Response  (extracted data + mentor feedback)
    |
    v
Streamlit UI  (renders feedback to the user)
```

---

## Tech Stack

| Layer       | Technology              |
|-------------|------------------------|
| Frontend    | Streamlit               |
| Backend     | FastAPI                 |
| Agent       | LangGraph               |
| LLM         | Groq (Llama 3.1 8B)    |
| Deployment  | Render                  |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A Groq API key — get one free at https://console.groq.com/keys
- A GitHub Personal Access Token — generate one at https://github.com/settings/tokens (scope: `public_repo`)

### Installation

```bash
# Clone the repository
git clone https://github.com/14-himanshu/student-github-reviewer.git
cd student-github-reviewer

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Open .env and add your API keys
```

### Running Locally

Start the backend (which also serves the frontend):

```bash
uvicorn main:app --reload
```

Then open your browser and navigate to `http://localhost:8000` to view the application!

---

## API Reference

### GET /

Health check endpoint.

**Response:**
```json
{ "message": "GitHub Reviewer backend is running perfectly!" }
```

### POST /review

Analyzes a GitHub user's portfolio and returns AI mentor feedback.

**Query Parameter:**

| Parameter  | Type   | Description              |
|------------|--------|--------------------------|
| `username` | string | GitHub username to review |

**Example:**
```bash
curl -X POST "https://student-github-reviewer-yraz.onrender.com/review?username=torvalds"
```

**Response:**
```json
{
  "username": "torvalds",
  "extracted_data": {
    "avatar_url": "https://avatars.githubusercontent.com/u/1024025?v=4",
    "followers": 200000,
    "recent_repos": ["linux", "subsurface-for-dirk"],
    "primary_languages": ["C", "C++"],
    "public_repos_count": 7,
    "repo_readmes": {
       "linux": "Linux kernel..."
    }
  },
  "mentor_feedback": "[GRADE: A+]\n[BADGES: C Master, Open Source Legend]\n\nYour expertise in C is evident..."
}
```

### POST /cover-letter

Generates a professional cover letter based on cached GitHub data. Must be called after `/review`.

**Query Parameter:**

| Parameter  | Type   | Description              |
|------------|--------|--------------------------|
| `username` | string | GitHub username to review |

**Example:**
```bash
curl -X POST "https://student-github-reviewer-yraz.onrender.com/cover-letter?username=torvalds"
```

**Response:**
```json
{
  "cover_letter": "Dear Hiring Manager, ..."
}
```

---

## Project Structure

```
student-github-reviewer/
├── agent/
│   ├── __init__.py        # Package initializer
│   ├── graph.py           # LangGraph workflow
│   ├── nodes.py           # Agent node functions
│   └── state.py           # State schema
├── ui/
│   └── app.py             # Streamlit frontend
├── main.py                # FastAPI entry point
├── requirements.txt       # Dependencies
├── .env.example           # Environment variable template
├── render.yaml            # Render deployment config
├── .gitignore
├── LICENSE
└── README.md
```

---

## Deployment

This project is deployed as two separate services on Render:

| Service  | Name                    | URL                                                |
|----------|-------------------------|----------------------------------------------------|
| Backend  | `github-reviewer-api`   | https://student-github-reviewer-yraz.onrender.com  |
| Frontend | `github-reviewer-ui`    | https://github-reviewer-ui-p5e6.onrender.com       |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Built by [Himanshu Pandey](https://github.com/14-himanshu)
