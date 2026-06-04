import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON
from .database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, index=True)
    github_data = Column(JSON)
    feedback_markdown = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
