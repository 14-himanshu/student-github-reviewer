import streamlit as st
import requests
import json

st.set_page_config(
    page_title="GitHub Portfolio Reviewer",
    page_icon="https://github.githubassets.com/favicons/favicon.png",
    layout="centered",
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## About")
    st.markdown(
        "This tool analyzes a GitHub profile and provides "
        "AI-generated mentorship feedback using **Groq / Llama 3.1**."
    )
    st.divider()
    st.markdown("**How it works**")
    st.markdown("1. Enter a GitHub username")
    st.markdown("2. The backend fetches their repositories")
    st.markdown("3. An AI Code Mentor reviews the portfolio")
    st.markdown("4. You get a detailed, actionable feedback report")
    st.divider()
    st.caption("Built with FastAPI · LangGraph · Streamlit · Render")

# --- Header ---
st.title("GitHub Portfolio Reviewer")
st.markdown("Enter a GitHub username below to get an AI-powered code mentor review.")
st.divider()

# --- Input ---
col1, col2 = st.columns([3, 1])
with col1:
    username = st.text_input(
        "GitHub Username",
        placeholder="e.g. torvalds",
        label_visibility="collapsed",
    )
with col2:
    analyze = st.button("Analyze", use_container_width=True, type="primary")

# --- Analysis ---
if analyze:
    if not username.strip():
        st.warning("Please enter a GitHub username to continue.")
    else:
        with st.spinner(f"Fetching data for **{username}**..."):
            try:
                response = requests.post(
                    f"https://student-github-reviewer-yraz.onrender.com/review?username={username}",
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    extracted = data.get("extracted_data", {})
                    feedback = data.get("mentor_feedback", "")

                    st.success("Analysis complete.")
                    st.divider()

                    # --- GitHub Stats ---
                    st.subheader("GitHub Overview")

                    repos = extracted.get("recent_repos", [])
                    languages = extracted.get("primary_languages", [])
                    repo_count = extracted.get("public_repos_count", 0)

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Public Repos", repo_count)
                    m2.metric("Languages Used", len(languages))
                    m3.metric("Recent Repos Reviewed", len(repos))

                    st.divider()

                    # --- Recent Repos ---
                    with st.expander("Recent Repositories", expanded=True):
                        if repos:
                            for repo in repos:
                                st.markdown(
                                    f"- [{repo}](https://github.com/{username}/{repo})"
                                )
                        else:
                            st.write("No repositories found.")

                    # --- Languages ---
                    with st.expander("Languages Detected"):
                        if languages:
                            st.write(", ".join(languages))
                        else:
                            st.write("No language data available.")

                    st.divider()

                    # --- AI Feedback ---
                    st.subheader("Mentor Feedback")
                    st.markdown(feedback)

                elif response.status_code == 404:
                    st.error(f"GitHub user `{username}` was not found. Please check the username and try again.")
                else:
                    st.error(f"Backend returned an error (status {response.status_code}). Please try again.")

            except requests.exceptions.Timeout:
                st.error("The request timed out. The backend may be spinning up — please wait a moment and try again.")
            except Exception as e:
                st.error(f"Could not connect to the backend: {e}")