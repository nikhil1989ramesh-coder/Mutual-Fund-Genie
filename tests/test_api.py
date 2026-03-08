"""
Unit Tests for Phase-4 Backend API (main.py)
Tests FastAPI endpoints using TestClient (no live server needed).
Run with: pytest tests/test_api.py -v
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the backend to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
API_DIR = os.path.join(BASE_DIR, 'Phase-4_Backend_API')
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, API_DIR)


# ── Mock heavy imports before loading main.py ──────────────────────────────
# This prevents the app from loading FAISS / embedding models during testing
mock_rag = MagicMock()
mock_rag.generate_answer = MagicMock(return_value=("HDFC Flexi Cap has a 1% exit load.", ["https://hdfcmf.com"]))
mock_scheduler = MagicMock()

with patch.dict('sys.modules', {
    'Phase_3_Query_Generation.rag_agent': MagicMock(MutualFundRAG=MagicMock(return_value=mock_rag)),
    'Phase_5_Scheduler.scheduler': MagicMock(start_scheduler=MagicMock(return_value=mock_scheduler)),
    'faiss': MagicMock(),
    'sentence_transformers': MagicMock(),
}):
    from fastapi.testclient import TestClient

    # Patch the constructor so rag_agent = mock_rag
    with patch('Phase_3_Query_Generation.rag_agent.MutualFundRAG', return_value=mock_rag):
        # Patch start_scheduler
        with patch('Phase_5_Scheduler.scheduler.start_scheduler', return_value=mock_scheduler):
            try:
                from Phase_4_Backend_API.main import app  # noqa: E402
            except Exception:
                # Fallback import path
                sys.path.insert(0, API_DIR)
                from main import app  # noqa: E402

    client = TestClient(app)


# ── /api/chat  ──────────────────────────────────────────────────────────────
class TestChatEndpoint:

    def test_valid_message_returns_answer(self):
        mock_rag.generate_answer.return_value = ("HDFC Flexi Cap exit load is 1%.", ["https://hdfcmf.com"])
        response = client.post("/api/chat", json={"message": "What is the exit load?"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        assert "sources" in data
        assert isinstance(data["sources"], list)

    def test_empty_message_returns_400(self):
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 400
        assert "Empty message" in response.json()["detail"]

    def test_whitespace_message_returns_400(self):
        response = client.post("/api/chat", json={"message": "   "})
        assert response.status_code == 400

    def test_missing_message_field_returns_422(self):
        response = client.post("/api/chat", json={})
        assert response.status_code == 422

    def test_internal_error_returns_500(self):
        mock_rag.generate_answer.side_effect = Exception("Model crashed")
        response = client.post("/api/chat", json={"message": "What is NAV?"})
        assert response.status_code == 500
        # Reset side effect
        mock_rag.generate_answer.side_effect = None
        mock_rag.generate_answer.return_value = ("HDFC answer.", [])


# ── /api/faq  ───────────────────────────────────────────────────────────────
class TestFAQEndpoint:

    def test_faq_returns_list(self):
        mock_rag.generate_answer.return_value = (
            "1. What is exit load?\n2. What is SIP?\n3. What is NAV?", []
        )
        response = client.get("/api/faq")
        assert response.status_code == 200
        data = response.json()
        assert "faqs" in data
        assert isinstance(data["faqs"], list)
        assert len(data["faqs"]) <= 3

    def test_faq_returns_fallback_on_error(self):
        mock_rag.generate_answer.side_effect = Exception("LLM error")
        response = client.get("/api/faq")
        assert response.status_code == 200  # Always returns 200 with fallback
        data = response.json()
        assert "faqs" in data
        assert len(data["faqs"]) > 0
        # Reset
        mock_rag.generate_answer.side_effect = None
        mock_rag.generate_answer.return_value = ("HDFC answer.", [])


# ── Health / Basic Connectivity ─────────────────────────────────────────────
class TestAPIBasics:

    def test_docs_endpoint_accessible(self):
        """Verify FastAPI auto-generated docs are reachable."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_accessible(self):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Mutual Fund RAG API"
