from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class ReviewState(TypedDict):
    username: str
    github_data: dict
    feedback: str
    leetcode: str
    stackoverflow: str
    messages: Annotated[Sequence[BaseMessage], operator.add]