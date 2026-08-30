import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from backend.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_portfolio_reviews.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_home():
    # It might fail if frontend/index.html isn't present in CI, but assuming it exists
    response = client.get("/")
    assert response.status_code == 200

def test_review_missing_username():
    response = client.post("/review")
    assert response.status_code == 422 # Unprocessable Entity

def test_cover_letter_no_cache():
    response = client.post("/cover-letter?username=testuser")
    assert response.status_code == 400
    assert "User data not found in cache" in response.json()["detail"]
