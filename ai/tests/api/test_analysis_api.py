from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest

from app.main import app
from services.case_analysis_service import CaseAnalysisService
from app.api.schemas.analysis import CaseAnalysisResult

from app.api.dependencies import get_case_analysis_service

client = TestClient(app)

@pytest.fixture
def mock_case_analysis_service():
    with patch('app.api.dependencies.get_case_analysis_service') as mock_get_service:
        mock_service_instance = MagicMock(spec=CaseAnalysisService)
        mock_get_service.return_value = mock_service_instance
        yield mock_service_instance

@pytest.fixture(autouse=True)
def override_dependency(mock_case_analysis_service):
    # 의존성 오버라이드 등록
    app.dependency_overrides[get_case_analysis_service] = lambda: mock_case_analysis_service
    yield
    app.dependency_overrides.clear()

def test_analyze_case_success(mock_case_analysis_service):
    # 1) CaseAnalysisResult 인스턴스로 모킹
    mocked_report = CaseAnalysisResult(
        issues=["Issue 1", "Issue 2"],
        opinion="Mock opinion",
        expected_sentence="Mock sentence",
        confidence=0.99,
        references={},
        tags=[],
        recommendedLawyers=[]
    )
    mock_case_analysis_service.analyze_case.return_value = {
        "case_analysis": mocked_report
    }

    # 2) 올바른 요청 바디
    request_body = {
        "case": {
            "title": "Some title",
            "summary": "Some summary",
            "fullText": "Test fullText"
        }
    }

    # 3) API 호출
    response = client.post("/api/analysis", json=request_body)

    # 4) 응답 검증
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "report": {
                "issues": ["Issue 1", "Issue 2"],
                "opinion": "Mock opinion",
                "expected_sentence": "Mock sentence",
                "confidence": 0.99,
                "references": {},
                "tags": [],
                "recommendedLawyers": []
            },
            "tags": [],
            "recommendedLawyers": []
        }
    }

    # 5) 서비스 호출 인자 검증
    mock_case_analysis_service.analyze_case.assert_called_once_with(user_query="Test fullText")

def test_analyze_case_internal_error(mock_case_analysis_service):
    # 서비스 레이어가 예외를 던지도록 모킹
    mock_case_analysis_service.analyze_case.side_effect = Exception("Internal service error")

    # 올바른 요청 바디 형태로 변경
    request_body = {
        "case": {
            "title": "Error title",
            "summary": "Error summary",
            "fullText": "Test query for error"
        }
    }

    response = client.post("/api/analysis", json=request_body)

    # 이제 서비스 내부 예외로 인해 500 에러가 내려와야 합니다.
    assert response.status_code == 500
    assert "Internal service error" in response.json()["detail"]

def test_analyze_case_invalid_input():
    response = client.post(
        "/api/analysis",
        json={
            "invalid_field": "Test query"
        }
    )

    assert response.status_code == 422  # Unprocessable Entity
    assert "detail" in response.json()
    # 'case' 필드가 없다고 나와야 합니다
    assert response.json()["detail"][0]["loc"] == ["body", "case"]
