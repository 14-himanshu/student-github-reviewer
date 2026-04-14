from langgraph.graph import StateGraph, END
from .state import ReviewState
from .nodes import extract_github_data, code_mentor_review

# Build the LangGraph workflow
workflow = StateGraph(ReviewState)

# Add nodes (each node is an agent "step")
workflow.add_node("extract_github_data", extract_github_data)
workflow.add_node("code_mentor_review", code_mentor_review)

# Define the edges (the order of execution)
workflow.set_entry_point("extract_github_data")
workflow.add_edge("extract_github_data", "code_mentor_review")
workflow.add_edge("code_mentor_review", END)

# Compile the graph into a runnable app
github_reviewer_app = workflow.compile()
