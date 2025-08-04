import pytest
from fastapi.testclient import TestClient
from app.main import app
from services.consultation_service import ConsultationService
from app.api.dependencies import get_consultation_service
from unittest.mock import AsyncMock

# 테스트용 클라이언트
client = TestClient(app)

@pytest.fixture
def mock_llm_client():
    """LLM 클라이언트 모의 객체"""
    return AsyncMock()

def test_consultation_service_instance(mock_llm_client):
    """ConsultationService가 정상적으로 인스턴스화되는지 테스트"""
    service = ConsultationService(llm_client=mock_llm_client)
    assert isinstance(service, ConsultationService)
    assert service.llm_client == mock_llm_client

def test_create_consultation_application_endpoint():
    """POST /api/consult/application 엔드포인트의 기본 동작을 테스트"""
    # Given: 테스트용 요청 데이터
    request_data = {
        "case": {
            "title": "사기 피해 사건",
            "summary": "OOO가 금품을 편취한 사건",
            "fullText": "2025년 5월…"
        },
        "desiredOutcome": "무죄 주장",
        "weakPoints": "현장 증인이 부족하다."
    }

    # When: API 엔드포인트 호출
    response = client.post("/api/consult", json=request_data)

    # Then: 성공 응답 및 스텁 데이터 검증
    assert response.status_code == 200
