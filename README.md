# 🎓 Student GitHub Reviewer

> **An AI-powered tool that analyzes a student's GitHub portfolio and delivers personalized mentorship feedback.**

Built with **FastAPI**, **LangGraph**, and **Groq (Llama 3.1)** — this project fetches a user's GitHub profile & repositories, then uses an AI "Code Mentor" agent to review their work and suggest improvements.

---

## ✨ Features

- 🔍 **GitHub Data Extraction** — Fetches recent repositories, languages, and profile stats via the GitHub API.
- 🤖 **AI Mentor Feedback** — Uses Groq's Llama 3.1 model to generate encouraging, actionable code reviews.
- 🔗 **LangGraph Agent Pipeline** — Orchestrates the review as a multi-step agent graph (extract → review).
- ⚡ **FastAPI Backend** — Clean, fast REST API with automatic Swagger docs.

---

## 🏗️ Architecture

```
User Request
    │
    ▼
┌──────────────────┐
│   FastAPI Server  │  ← POST /review?username=...
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│        LangGraph Pipeline        │
│                                  │
│  ┌────────────────────────────┐  │
│  │  1. extract_github_data    │  │  → GitHub API
│  └─────────────┬──────────────┘  │
│                │                 │
│  ┌─────────────▼──────────────┐  │
│  │  2. code_mentor_review     │  │  → Groq / Llama 3.1
│  └────────────────────────────┘  │
└──────────────────────────────────┘
         │
         ▼
   JSON Response (data + feedback)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- A free [Groq API key](https://console.groq.com/keys)
- A [GitHub Personal Access Token](https://github.com/settings/tokens) (optional, but recommended to avoid rate limits)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/student-github-reviewer.git
cd student-github-reviewer

# 2. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Then open .env and paste your API keys
```

### Run the Server

```bash
uvicorn main:app --reload
```

The API will be live at **http://127.0.0.1:8000**  
📖 Interactive docs: **http://127.0.0.1:8000/docs**

---

## 📡 API Endpoints

| Method | Endpoint  | Description                        |
|--------|-----------|------------------------------------|
| GET    | `/`       | Health check                       |
| POST   | `/review` | Analyze a GitHub user's portfolio |

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/review?username=torvalds"
```

### Example Response

```json
{
  "username": "torvalds",
  "extracted_data": {
    "recent_repos": ["linux", "subsurface-for-dirk", "..."],
    "primary_languages": ["C", "C++"],
    "public_repos_count": 7
  },
  "mentor_feedback": "Great work! Your expertise in C is evident from..."
}
```

---

## 📁 Project Structure

```
student-github-reviewer/
├── agent/
│   ├── __init__.py        # Package initializer
│   ├── graph.py           # LangGraph workflow definition
│   ├── nodes.py           # Agent node functions (extract, review)
│   └── state.py           # TypedDict state schema
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Files excluded from version control
├── LICENSE                # MIT License
└── README.md              # You are here!
```

---

## 🛠️ Tech Stack

| Technology   | Purpose                       |
|-------------|-------------------------------|
| FastAPI     | REST API framework            |
| LangGraph   | Agent orchestration           |
| LangChain   | LLM integration layer         |
| Groq        | LLM inference (Llama 3.1)    |
| Python      | Core language                 |

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for blazing-fast LLM inference
- [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework

---

<p align="center">
  Made with ❤️ by <strong>Himanshu Pandey</strong>
</p>
