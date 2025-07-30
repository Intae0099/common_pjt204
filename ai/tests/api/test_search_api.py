# tests/api/test_search_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_search_service
from services.search_service import SearchService
from unittest.mock import AsyncMock
from datetime import date

from app.api.exceptions import ResourceNotFoundException

# TestClient 인스턴스 생성
client = TestClient(app)

# SearchService를 모킹하기 위한 fixture
@pytest.fixture
def mock_search_service():
    service = AsyncMock(spec=SearchService)
    app.dependency_overrides[get_search_service] = lambda: service
    yield service
    app.dependency_overrides = {}

# CaseSnippet와 유사한 Mock 객체 정의
class MockCaseSnippet:
    def __init__(self, case_id, title, decision_date, category, issue, summary, full_text):
        self.case_id = case_id
        self.title = title
        self.decision_date = decision_date
        self.category = category
        self.issue = issue
        self.summary = summary
        self.full_text = full_text

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockCaseDetail:
    def __init__(self, case_id, title, decision_date, category, issue, summary, full_text, statutes, precedents):
        self.case_id = case_id
        self.title = title
        self.decision_date = decision_date
        self.category = category
        self.issue = issue
        self.summary = summary
        self.full_text = full_text
        self.statutes = statutes
        self.precedents = precedents

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)


def test_search_cases_success(mock_search_service):
    # Mocking vector_search method
    mock_search_service.vector_search.return_value = (
        [
            MockCaseSnippet(
                    case_id="1",
                    title="사기죄 판례",
                    decision_date=date(2023, 1, 1),
                    category="형사",
                    issue="사기죄 성립 요건",
                    summary="사기죄에 대한 중요한 판례입니다.",
                    full_text="사기죄에 대한 중요한 판례입니다. 상세 내용은 다음과 같습니다."
                )
        ],
        1  # total_count
    )

    response = client.get("/api/search/cases?keyword=사기&page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "pageMeta" in data["data"]
    assert len(data["data"]["items"]) == 1
    assert data["data"]["items"][0]["caseId"] == "1"
    assert data["data"]["pageMeta"]["total"] == 1


def test_search_cases_pagination(mock_search_service):
    # Mocking vector_search for pagination test
    mock_search_service.vector_search.return_value = (
        [
            MockCaseSnippet(
                case_id=str(i),
                title=f"판례 {i}",
                decision_date=date(2023, 1, 1),
                category="민사",
                issue=f"판례 {i} 쟁점",
                summary=f"판례 {i} 요약",
                full_text=f"판례 {i} 전문"
            ) for i in range(1, 11)
        ],
        20  # total_count
    )

    response = client.get("/api/search/cases?keyword=테스트&page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) == 10
    assert data["data"]["pageMeta"]["total"] == 20
    assert data["data"]["pageMeta"]["page"] == 1
    assert data["data"]["pageMeta"]["size"] == 10
    assert data["data"]["pageMeta"]["hasNext"] is True

    mock_search_service.vector_search.return_value = (
        [
            MockCaseSnippet(
                case_id=str(i),
                title=f"판례 {i}",
                decision_date=date(2023, 1, 1),
                category="민사",
                issue=f"판례 {i} 쟁점",
                summary=f"판례 {i} 요약",
                full_text=f"판례 {i} 전문"
            ) for i in range(11, 21)
        ],
        20  # total_count
    )
    response = client.get("/api/search/cases?keyword=테스트&page=2&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) == 10
    assert data["data"]["pageMeta"]["total"] == 20
    assert data["data"]["pageMeta"]["page"] == 2
    assert data["data"]["pageMeta"]["size"] == 10
    assert data["data"]["pageMeta"]["hasNext"] is False


def test_search_cases_invalid_keyword():
    response = client.get("/api/search/cases?keyword=a")
    assert response.status_code == 400  # Custom handler maps 422 to 400
    data = response.json()
    assert "error" in data


def test_get_case_detail_success(mock_search_service):
    # Mocking get_case_by_id method
    mock_search_service.get_case_by_id.return_value = MockCaseDetail(
        case_id="12345",
        title="소유권이전등기말소",
        decision_date=date(1978, 4, 11),
        category="민사",
        issue="소유권이전등기말소 쟁점",
        summary="소유권이전등기말소 요약",
        full_text="<판례 전문 원문...>",
        statutes="농지개혁법; 민법",
        precedents="2012도1234; 2015도9876"
    )

    response = client.get("/api/cases/12345")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["caseId"] == "12345"
    assert data["data"]["statutes"] == "농지개혁법; 민법"
    assert data["data"]["precedents"] == "2012도1234; 2015도9876"


def test_get_case_detail_not_found(mock_search_service):
    # Mocking get_case_by_id to return None (not found)
    mock_search_service.get_case_by_id.return_value = None

    response = client.get("/api/cases/nonexistent_id")
    assert response.status_code == 404
    data = response.json()
    assert "success" in data and data["success"] is False
    assert "error" in data
    assert data["error"]["message"] == "해당 ID의 판례를 찾을 수 없습니다."
