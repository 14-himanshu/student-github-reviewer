import os
import streamlit as st
import requests
import re

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

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
        st.session_state["analyzed_username"] = username.strip()

if st.session_state.get("analyzed_username"):
    username = st.session_state["analyzed_username"]
    with st.spinner(f"Fetching data for **{username}**..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/review?username={username}",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                    timeout=120,
                )

                if response.status_code == 200:
                    data = response.json()
                    extracted = data.get("extracted_data", {})
                    feedback = data.get("mentor_feedback", "")

                    st.success("Analysis complete.")
                    st.divider()

                    # --- GitHub Stats ---
                    avatar_url = extracted.get("avatar_url", "")
                    followers = extracted.get("followers", 0)

                    col_img, col_txt = st.columns([1, 4])
                    with col_img:
                        if avatar_url:
                            st.image(avatar_url, width=100)
                    with col_txt:
                        st.subheader(f"Overview for {username}")
                        st.write(f"**Followers:** {followers}")

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
                    # Parse Grade and Badges
                    grade_match = re.search(r"\[GRADE:\s*(.*?)\]", feedback)
                    badges_match = re.search(r"\[BADGES:\s*(.*?)\]", feedback)
                    
                    grade = grade_match.group(1).strip() if grade_match else None
                    badges = badges_match.group(1).strip() if badges_match else None
                    
                    # Clean feedback text
                    clean_feedback = re.sub(r"\[GRADE:\s*.*?\]", "", feedback)
                    clean_feedback = re.sub(r"\[BADGES:\s*.*?\]", "", clean_feedback).strip()

                    st.subheader("Mentor Feedback")
                    if grade or badges:
                        g_col, b_col = st.columns([1, 4])
                        with g_col:
                            if grade:
                                st.metric("Overall Grade", grade)
                        with b_col:
                            if badges:
                                st.write("**Awarded Badges:**")
                                # Display badges as inline markdown code snippets
                                badges_list = [b.strip() for b in badges.split(",")]
                                badges_md = " ".join([f"`🏆 {b}`" for b in badges_list])
                                st.markdown(badges_md)
                        st.divider()

                    st.markdown(clean_feedback)

                    st.divider()
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button(
                            label="Download Report (Markdown)",
                            data=clean_feedback,
                            file_name=f"{username}_portfolio_review.md",
                            mime="text/markdown",
                            type="primary"
                        )
                    with c2:
                        if st.button("Generate PDF Resume"):
                            with st.spinner("Generating PDF..."):
                                try:
                                    pdf_resp = requests.post(f"{BACKEND_URL}/generate-pdf?username={username}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=60)
                                    if pdf_resp.status_code == 200:
                                        st.download_button(
                                            label="Click to Download PDF",
                                            data=pdf_resp.content,
                                            file_name=f"{username}_resume.pdf",
                                            mime="application/pdf",
                                            type="primary"
                                        )
                                    else:
                                        st.error("Failed to generate PDF.")
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")

                    # --- Career Tools ---
                    st.subheader("Career Tools")
                    with st.expander("📄 Generate Cover Letter"):
                        st.write("Generate a professional cover letter based on your GitHub portfolio.")
                        if st.button("Generate Now", key="btn_cover_letter"):
                            with st.spinner("Writing your cover letter..."):
                                try:
                                    cl_resp = requests.post(f"{BACKEND_URL}/cover-letter?username={username}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=60)
                                    if cl_resp.status_code == 200:
                                        cl_data = cl_resp.json().get("cover_letter", "")
                                        st.text_area("Your Cover Letter", value=cl_data, height=300)
                                        st.download_button("Download Cover Letter", data=cl_data, file_name=f"{username}_cover_letter.md")
                                    elif cl_resp.status_code == 429:
                                        st.warning("Rate limit exceeded. Please try again later.")
                                    else:
                                        st.error(f"Failed to generate cover letter. (Status {cl_resp.status_code})")
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")

                    with st.expander("🗺️ Skill Gap Analysis & Roadmap"):
                        st.write("Get a customized 3-step learning roadmap to level up your skills.")
                        if st.button("Generate Roadmap", key="btn_roadmap"):
                            with st.spinner("Analyzing your skills..."):
                                try:
                                    rm_resp = requests.post(f"{BACKEND_URL}/roadmap?username={username}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=60)
                                    if rm_resp.status_code == 200:
                                        rm_data = rm_resp.json().get("roadmap", "")
                                        st.markdown(rm_data)
                                    elif rm_resp.status_code == 429:
                                        st.warning("Rate limit exceeded. Please try again later.")
                                    else:
                                        st.error(f"Failed to generate roadmap. (Status {rm_resp.status_code})")
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")

                    with st.expander("💡 Project Idea Generator"):
                        st.write("Get 3 specific project ideas tailored to complement your existing portfolio.")
                        if st.button("Generate Ideas", key="btn_ideas"):
                            with st.spinner("Brainstorming projects..."):
                                try:
                                    pi_resp = requests.post(f"{BACKEND_URL}/project-ideas?username={username}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=60)
                                    if pi_resp.status_code == 200:
                                        pi_data = pi_resp.json().get("ideas", "")
                                        st.markdown(pi_data)
                                    elif pi_resp.status_code == 429:
                                        st.warning("Rate limit exceeded. Please try again later.")
                                    else:
                                        st.error(f"Failed to generate project ideas. (Status {pi_resp.status_code})")
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")

                    with st.expander("🎯 Mock Interview Questions"):
                        st.write("Get 5 tailored technical interview questions based on your top languages.")
                        if st.button("Generate Questions", key="btn_interview"):
                            with st.spinner("Preparing questions..."):
                                try:
                                    iq_resp = requests.post(f"{BACKEND_URL}/interview-prep?username={username}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=60)
                                    if iq_resp.status_code == 200:
                                        iq_data = iq_resp.json().get("questions", "")
                                        st.markdown(iq_data)
                                    elif iq_resp.status_code == 429:
                                        st.warning("Rate limit exceeded. Please try again later.")
                                    else:
                                        st.error(f"Failed to generate interview questions. (Status {iq_resp.status_code})")
                                except Exception as e:
                                    st.error(f"Error connecting to backend: {e}")

                    with st.expander("🔍 Deep Dive Repo Analysis"):
                        st.write("Get a comprehensive review of a specific repository.")
                        recent_repos = extracted.get("recent_repos", [])
                        if not recent_repos:
                            st.info("No recent public repositories found for this user.")
                        else:
                            selected_repo = st.selectbox("Select a repository:", recent_repos)
                            if st.button("Run Deep Dive", key="btn_deep_dive"):
                                with st.spinner(f"Analyzing {selected_repo}..."):
                                    try:
                                        dd_resp = requests.post(f"{BACKEND_URL}/repo-deep-dive?username={username}&repo_name={selected_repo}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=60)
                                        if dd_resp.status_code == 200:
                                            dd_data = dd_resp.json().get("deep_dive", "")
                                            st.markdown(dd_data)
                                        elif dd_resp.status_code == 429:
                                            st.warning("Rate limit exceeded. Please try again later.")
                                        else:
                                            st.error(f"Failed to generate deep dive. (Status {dd_resp.status_code})")
                                    except Exception as e:
                                        st.error(f"Error connecting to backend: {e}")

                elif response.status_code == 404:
                    st.error(f"GitHub user `{username}` was not found. Please check the username and try again.")
                elif response.status_code == 429:
                    st.warning(
                        "⚠️ The AI service is currently rate-limited (too many requests). "
                        "Please wait 30–60 seconds and try again."
                    )
                else:
                    st.error(f"Backend returned an error (status {response.status_code}). Please try again.")

            except requests.exceptions.Timeout:
                st.error("The request timed out. The backend may be spinning up — please wait a moment and try again.")
            except Exception as e:
                st.error(f"Could not connect to the backend: {e}")