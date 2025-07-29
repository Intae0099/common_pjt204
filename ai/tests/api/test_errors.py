import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_case_analysis_service
client = TestClient(app)

def test_analyze_case_missing_param():
    # 400을 보려면 인증을 통과시켜야 함
    response = client.post("/api/analysis", json={}, headers={"Authorization": "Bearer test"})
    assert response.status_code == 400
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"]["code"] == "INVALID_PARAM"

# def test_analyze_case_unauthorized():
#     # 헤더 없이 → 401
#     response = client.post("/api/analysis", json={"case": {"fullText": "test"}})
#     assert response.status_code == 401
#     json_response = response.json()
#     assert json_response["success"] is False
#     assert json_response["error"]["code"] == "UNAUTHORIZED"

def test_analyze_case_not_found():
    # This endpoint doesn't have a not found case, so we'll simulate it
    # by calling a non-existent endpoint.
    response = client.get("/api/non_existent_endpoint")
    assert response.status_code == 404
    json_response = response.json()
    assert json_response["success"] is False
    assert json_response["error"]["code"] == "NOT_FOUND"

def test_analyze_case_server_error():
    # 1) analyze_case가 일반 예외를 던지도록 서비스 오버라이드
    class BoomService:
        def analyze_case(self, user_query: str):
            raise RuntimeError("boom")

    app.dependency_overrides[get_case_analysis_service] = lambda: BoomService()

    try:
        # 2) 이 테스트에서만 서버 예외를 re-raise하지 않는 클라이언트 사용
        with TestClient(app, raise_server_exceptions=False) as client:
            # 3) 유효한 본문 + 인증 헤더로 호출 (검증/권한 통과)
            response = client.post(
                "/api/analysis",
                json={"case": {"title": "t", "summary": "s", "fullText": "trigger 500"}},
                headers={"Authorization": "Bearer test"},
            )

        # 4) 500 + 공통 에러 포맷 확인
        assert response.status_code == 500
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "SERVER_ERROR"
        assert "message" in body["error"]
    finally:
        # 5) 오버라이드 해제(다른 테스트 영향 방지)
        app.dependency_overrides.clear()