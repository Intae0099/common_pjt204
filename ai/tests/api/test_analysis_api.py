from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest

from ai.app.main import app
from ai.services.case_analysis_service import CaseAnalysisService
from ai.llm import Gpt4oMini
from ai.llm.llm_response_parser import CaseAnalysisResult # CaseAnalysisResult 임포트

from ai.app.api.dependencies import get_case_analysis_service

client = TestClient(app)

@pytest.fixture
def mock_case_analysis_service():
    with patch('ai.app.api.dependencies.get_case_analysis_service') as mock_get_service:
        mock_service_instance = MagicMock(spec=CaseAnalysisService)
        mock_get_service.return_value = mock_service_instance
        yield mock_service_instance

@pytest.fixture
def mock_llm():
    with patch('ai.app.api.dependencies.get_llm') as mock_get_llm:
        mock_llm_instance = MagicMock(spec=Gpt4oMini)
        mock_get_llm.return_value = mock_llm_instance
        yield mock_llm_instance


@pytest.fixture(autouse=True)
def override_dependency(mock_case_analysis_service):
    # TestClient 생성 전에, 또는 바로 다음 줄에:
    app.dependency_overrides[get_case_analysis_service] = lambda: mock_case_analysis_service
    yield
    app.dependency_overrides.clear()

def test_analyze_case_success(mock_case_analysis_service):
    # CaseAnalysisResult 객체의 JSON 직렬화 형태와 동일한 딕셔너리로 모킹
    mock_case_analysis_service.analyze_case.return_value = {
        "case_analysis": {
            "issues": ["Issue 1", "Issue 2"],
            "opinion": "Mock opinion",
            "expected_sentence": "Mock sentence",
            "confidence": 0.99,
            "references": {},
            "tags": [],
            "recommendedLawyers": []
        },
    }

    response = client.post(
        "/api/analysis",
        json={
            "query": "Test query for analysis"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "case_analysis": {
            "issues": ["Issue 1", "Issue 2"],
            "opinion": "Mock opinion",
            "expected_sentence": "Mock sentence",
            "confidence": 0.99,
            "references": {},
            "tags": [],
            "recommendedLawyers": []
        }
    }
    mock_case_analysis_service.analyze_case.assert_called_once_with("Test query for analysis")

def test_analyze_case_internal_error(mock_case_analysis_service):
    mock_case_analysis_service.analyze_case.side_effect = Exception("Internal service error")

    response = client.post(
        "/api/analysis",
        json={
            "query": "Test query for error"
        }
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal service error"}

def test_analyze_case_invalid_input():
    response = client.post(
        "/api/analysis",
        json={
            "invalid_field": "Test query"
        }
    )

    assert response.status_code == 422 # Unprocessable Entity
    assert "detail" in response.json()
    assert response.json()["detail"][0]["loc"] == ["body", "query"]
