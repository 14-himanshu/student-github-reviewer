import streamlit as st
import requests
st.set_page_config(page_title="GitHub Code Mentor", page_icon="🐙")
st.title("🐙 The Student GitHub & Portfolio Reviewer")
username = st.text_input("GitHub Username:", placeholder="e.g., torvalds")
if st.button("Analyze Portfolio"):
    if username:
        with st.spinner(f"Analyzing {username}'s repositories..."):
            try:
                response = requests.post(f"https://student-github-reviewer-yraz.onrender.com/review?username={username}")
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete!")
                    st.json(data["extracted_data"])
                    st.write(data["mentor_feedback"])
                else:
                    st.error(f"Backend Error: {response.status_code}")
            except Exception as e:
                st.error("Could not connect to the backend.")