"""
E2E Integration Tests (Module 10).

Simulates the complete sourcing pipeline: uploading files, starting a job,
polling until complete, and retrieving ranking, insights, and exports.
"""

from __future__ import annotations

import io
import json
import uuid
import pytest
from unittest.mock import Mock, AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_store
from app.services.embedding import EmbeddingService
from app.services.pdf_extractor import PDFExtractorService
import numpy as np

# Mocking SentenceTransformer model to return perfect similarity (all ones)
class MockEmbedModel:
    def encode(self, texts, normalize_embeddings=True):
        shape = (len(texts), 384)
        arr = np.ones(shape, dtype=np.float32)
        if normalize_embeddings:
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            arr = arr / norms
        return arr

@pytest.fixture(autouse=True)
def mock_embedding():
    EmbeddingService._model = MockEmbedModel()

@pytest.fixture
def client():
    # Clear memory store for a clean test run
    store = get_store()
    store._files.clear()
    store._jobs.clear()
    store._jd_profiles.clear()
    store._resume_profiles.clear()
    store._semantic_profiles.clear()
    store._rankings.clear()
    store._recommendations.clear()
    return TestClient(app)

@pytest.mark.asyncio
async def test_e2e_integration_flow(client, monkeypatch):
    # ── MOCK PDF TEXT EXTRACTION ──
    monkeypatch.setattr(PDFExtractorService, "extract_text", lambda self, path: "Mock extracted PDF text content DevOps Kubernetes AWS")

    # ── MOCK GEMINI RESPONSES ──
    class MockJDResponse:
        def __init__(self):
            self.text = json.dumps({
                "job_title": "Senior DevOps Engineer",
                "industry": "Cloud",
                "seniority": "Senior",
                "required_skills": ["Kubernetes", "AWS"],
                "preferred_skills": ["Go"],
                "education": "Bachelor's Degree",
                "experience": "5 years",
                "certifications": ["AWS Solutions Architect"],
                "responsibilities": ["Maintain cluster", "CI/CD"],
                "soft_skills": ["Team player"],
                "keywords": ["DevOps"]
            })
            
    class MockResumeResponse:
        def __init__(self):
            self.text = json.dumps({
                "personal_information": {
                    "name": "Jane Doe",
                    "email": "jane@example.com"
                },
                "professional_information": {
                    "current_role": "DevOps Engineer",
                    "total_years_experience": 6.0
                },
                "skills": {
                    "technical_skills": ["Kubernetes", "Docker"],
                    "frameworks": [],
                    "languages": ["Python", "Go"],
                    "tools": ["Git"],
                    "cloud_platforms": ["AWS"],
                    "databases": ["PostgreSQL"],
                    "soft_skills": ["Communication"]
                },
                "experience": [
                    {
                        "company": "CloudCorp",
                        "job_title": "DevOps Engineer",
                        "start_date": "2020",
                        "end_date": "Present",
                        "description": "Kubernetes and AWS deployment",
                        "technologies_used": ["Kubernetes", "AWS"]
                    }
                ],
                "projects": [
                    {
                        "project_name": "ClusterMigration",
                        "description": "Migrated cluster to EKS",
                        "technologies": ["Kubernetes"]
                    }
                ],
                "education": [
                    {
                        "degree": "BSc Computer Science",
                        "institution": "State University",
                        "graduation_year": "2018"
                    }
                ],
                "certifications": [
                    {
                        "name": "AWS Solutions Architect",
                        "issuer": "Amazon",
                        "year": "2022"
                    }
                ]
            })

    class MockInsightResponse:
        def __init__(self):
            self.text = json.dumps({
                "overall_summary": "Highly qualified DevOps professional matching core credentials.",
                "top_strengths": ["Strong Kubernetes and AWS match"],
                "top_weaknesses": ["None"],
                "matched_skills": ["Kubernetes", "AWS"],
                "missing_skills": [],
                "relevant_projects": ["Migrated cluster to EKS"],
                "experience_highlights": ["6 years as DevOps Engineer at CloudCorp"],
                "education_summary": "BSc Computer Science",
                "certification_summary": "AWS Solutions Architect",
                "interview_focus_areas": [],
                "hiring_recommendation": "Strong Fit"
            })

    def mock_routing(contents, **kwargs):
        check_str = str(contents) + str(kwargs)
        if "JDProfileBase" in check_str:
            return MockJDResponse()
        elif "ResumeProfileBase" in check_str:
            return MockResumeResponse()
        else:
            return MockInsightResponse()

    async def mock_generate_content_async(contents, **kwargs):
        return mock_routing(contents, **kwargs)

    # Mock generative AI model generate_content methods dynamically based on input content
    mock_model = Mock()
    mock_model.generate_content = Mock(side_effect=mock_routing)
    mock_model.generate_content_async = AsyncMock(side_effect=mock_generate_content_async)
    
    # Patch GenerativeModel creation
    monkeypatch.setattr("google.generativeai.GenerativeModel", lambda *args, **kwargs: mock_model)

    # ── 1. UPLOAD FILES ──
    # JD
    jd_file = io.BytesIO(b"%PDF-1.4\nJob description text for Senior DevOps Engineer: Kubernetes, AWS required.")
    response = client.post(
        "/v1/files/upload",
        files={"file": ("jd.pdf", jd_file, "application/pdf")},
        data={"file_type": "job_description"}
    )
    assert response.status_code == 201
    jd_file_id = response.json()["data"]["id"]

    # Resume
    resume_file = io.BytesIO(b"%PDF-1.4\nJane Doe DevOps Resume. Kubernetes, AWS expert.")
    response = client.post(
        "/v1/files/upload",
        files={"file": ("resume.pdf", resume_file, "application/pdf")},
        data={"file_type": "resume"}
    )
    assert response.status_code == 201
    resume_file_id = response.json()["data"]["id"]

    # ── 2. CREATE JOB ──
    response = client.post(
        "/v1/analysis/jobs",
        json={
            "job_description_file_id": jd_file_id,
            "resume_file_ids": [resume_file_id]
        }
    )
    assert response.status_code == 202
    job_id = response.json()["data"]["id"]

    # ── 3. POLL STATUS UNTIL COMPLETE ──
    completed = False
    for _ in range(30):
        import asyncio
        await asyncio.sleep(0.1)
        
        status_res = client.get(f"/v1/analysis/jobs/{job_id}")
        assert status_res.status_code == 200
        job_status = status_res.json()["data"]["status"]
        if job_status == "completed":
            completed = True
            break
        elif job_status == "failed":
            pytest.fail(f"Pipeline failed: {status_res.json()['data']['error_message']}")

    assert completed, "Pipeline did not reach completed state in time"

    # ── 4. FETCH RESULTS & ANALYTICS ──
    # Ranking
    rank_res = client.get(f"/v1/analysis/jobs/{job_id}/ranking")
    assert rank_res.status_code == 200
    assert len(rank_res.json()["data"]["candidates"]) == 1
    cand_id = rank_res.json()["data"]["candidates"][0]["candidate_id"]

    # Insights
    insights_res = client.get(f"/v1/candidates/{cand_id}/insights")
    assert insights_res.status_code == 200
    assert insights_res.json()["data"]["insight"]["hiring_recommendation"] == "Strong Fit"

    # Analytics
    analytics_res = client.get(f"/v1/analysis/jobs/{job_id}/analytics")
    assert analytics_res.status_code == 200
    assert analytics_res.json()["data"]["analytics"]["candidates_reviewed"] == 1

    # Executive Summary
    exec_res = client.get(f"/v1/analysis/jobs/{job_id}/executive-summary")
    assert exec_res.status_code == 200
    assert "Senior DevOps Engineer" in exec_res.json()["data"]["executive_summary"]["executive_text_summary"]

    # ── 5. FETCH EXPORTS ──
    # Excel
    excel_res = client.get(f"/v1/analysis/jobs/{job_id}/export/excel")
    assert excel_res.status_code == 200
    assert len(excel_res.content) > 0

    # PDF
    pdf_res = client.get(f"/v1/analysis/jobs/{job_id}/export/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF")

    # JSON
    json_res = client.get(f"/v1/analysis/jobs/{job_id}/export/json")
    assert json_res.status_code == 200
    assert json_res.json()["data"]["job_id"] == job_id
