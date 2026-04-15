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

Start the backend:

```bash
uvicorn main:app --reload
```

In a separate terminal, start the frontend:

```bash
streamlit run ui/app.py
```

- Backend API: http://127.0.0.1:8000
- API Docs (Swagger): http://127.0.0.1:8000/docs
- Frontend UI: http://localhost:8501

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
    "recent_repos": ["linux", "subsurface-for-dirk"],
    "primary_languages": ["C", "C++"],
    "public_repos_count": 7
  },
  "mentor_feedback": "Your expertise in C is evident..."
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
