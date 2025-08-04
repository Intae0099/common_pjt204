# tests/api/test_analysis_api.py
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import pytest

from app.main import app
from services.case_analysis_service import CaseAnalysisService
from app.api.schemas.analysis import CaseAnalysisResult
from app.api.dependencies import get_case_analysis_service, get_current_user

# 전역 기본 클라이언트 (일반 테스트용)
client = TestClient(app)

# 1) 서비스 모킹 인스턴스
@pytest.fixture
def mock_case_analysis_service():
    return MagicMock(spec=CaseAnalysisService)

# 2) 의존성 오버라이드(인증 + 서비스) — 모든 테스트에 자동 적용
@pytest.fixture(autouse=True)
def overrides(mock_case_analysis_service):
    app.dependency_overrides[get_case_analysis_service] = lambda: mock_case_analysis_service
    app.dependency_overrides[get_current_user] = lambda: "user"  # 인증 우회
    yield
    # 개별 키만 해제 (다른 오버라이드에 영향 없도록)
    app.dependency_overrides.pop(get_case_analysis_service, None)
    app.dependency_overrides.pop(get_current_user, None)

def test_analyze_case_success(mock_case_analysis_service):
    # 1) 서비스 반환값 모킹
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

    # 3) 호출
    resp = client.post("/api/analysis", json=request_body)

    # 4) 검증 (공통 성공 규격)
    assert resp.status_code == 200
    assert resp.json() == {
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
            }
        }
    }
    mock_case_analysis_service.analyze_case.assert_called_once_with(user_query="Test fullText")

def test_analyze_case_internal_error(mock_case_analysis_service):
    # 일반 Exception으로 500 경로 유도 (APIException이 아님)
    mock_case_analysis_service.analyze_case.side_effect = Exception("Internal service error")

    request_body = {
        "case": {"title": "Error title", "summary": "Error summary", "fullText": "Test query for error"}
    }

    # 이 테스트에서만 서버 예외 재-던짐 방지
    with TestClient(app, raise_server_exceptions=False) as local_client:
        resp = local_client.post("/api/analysis", json=request_body)

    # 500 + 공통 실패 규격
    assert resp.status_code == 500
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "SERVER_ERROR"
    assert "message" in body["error"]  # 내부 메시지는 일반화되어 내려가는 설계

def test_analyze_case_invalid_input():
    # 유효성 실패는 설계상 400/INVALID_PARAM으로 통일
    resp = client.post("/api/analysis", json={"invalid_field": "Test query"})

    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_PARAM"
    # 세부 위치는 details 배열로 확인
    assert "details" in body
    assert any("case" in err.get("loc", []) for err in body["details"])
