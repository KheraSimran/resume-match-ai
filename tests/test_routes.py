import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
import io
from app.models.analysis import ResumeAnalysis

client = TestClient(app)

def test_health_check():
    """The simplest test — verify the health endpoint returns 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_rejects_non_pdf():
    """Verify we return 400 if someone uploads a non-PDF."""
    fake_file = io.BytesIO(b"this is not a pdf")
    
    response = client.post(
        "/api/v1/analyze",
        files={"resume": ("resume.txt", fake_file, "text/plain")},
        data={"job_description": "Python developer needed"}
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]

def test_analyze_rejects_empty_jd():
    """Verify we return 400 if job description is empty."""
    fake_pdf = io.BytesIO(b"%PDF fake content")

    response = client.post(
        "/api/v1/analyze",
        files={"resume": ("resume.pdf", fake_pdf, "application/pdf")},
        data={"job_description": "   "}  # whitespace only
    )
    assert response.status_code == 400

@patch("app.api.routes.extract_text_from_pdf")
@patch("app.api.routes.split_text_into_chunks")
@patch("app.api.routes.resume_jd_match")
def test_analyze_success(mock_analyze, mock_split, mock_extract):
    """
    Test the happy path with mocked services.
    """
    # Set up what our mocked functions should return
    mock_extract.return_value = "Python developer with Django experience"
    mock_split.return_value = [MagicMock()]
    mock_analyze.return_value = ResumeAnalysis (
        ats_score = 78,
        missing_keywords = ["FastAPI", "Docker"],
        rewritten_bullets = ["Built REST APIs", "Deployed with Docker"],
        score_explanation = "Good match but missing modern stack"
    )
    fake_pdf = io.BytesIO(b"%PDF fake")

    response = client.post(
        "/api/v1/analyze",
        files={"resume": ("resume.pdf", fake_pdf, "application/pdf")},
        data={"job_description": "We need a Python FastAPI developer"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["ats_score"] == 78
    assert "FastAPI" in data["data"]["missing_keywords"]