import streamlit as st
import requests
import json

st.set_page_config(page_title="GitHub Code Mentor", page_icon="🐙")
st.title("🐙 The Student GitHub & Portfolio Reviewer")

username = st.text_input("GitHub Username:", placeholder="e.g., torvalds")

if st.button("Analyze Portfolio"):
    if username:
        with st.spinner(f"Analyzing {username}'s repositories..."):
            try:
                response = requests.post(
                    f"https://student-github-reviewer-yraz.onrender.com/review?username={username}"
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete!")

                    # Display extracted GitHub data without dynamic JS components
                    st.subheader("📊 GitHub Data")
                    extracted = data.get("extracted_data", {})
                    st.code(json.dumps(extracted, indent=2), language="json")

                    # Display AI mentor feedback
                    st.subheader("🤖 Mentor Feedback")
                    st.markdown(data.get("mentor_feedback", ""))
                else:
                    st.error(f"Backend Error: {response.status_code}")
            except Exception as e:
                st.error(f"Could not connect to the backend: {e}")
    else:
        st.warning("Please enter a GitHub username.")