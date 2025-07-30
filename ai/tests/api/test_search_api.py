# tests/api/test_search_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_cases_success():
    response = client.get("/api/search/cases?keyword=사기")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "pageMeta" in data["data"]

def test_search_cases_invalid_keyword():
    response = client.get("/api/search/cases?keyword=a")
    assert response.status_code == 400  # Custom handler maps 422 to 400
    data = response.json()
    assert "error" in data

def test_get_case_detail_success():
    response = client.get("/api/cases/12345")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == 12345
    assert "references" in data["data"]

def test_get_case_detail_invalid_id():
    response = client.get("/api/cases/0")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
