from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_structure_case_success():
    response = client.post(
        "/api/cases/structuring",
        json={"freeText": "이것은 자유 서술된 사건 개요입니다. 중요한 내용이 포함되어 있습니다."}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "case" in response.json()["data"]
    assert "title" in response.json()["data"]["case"]
    assert "summary" in response.json()["data"]["case"]
    assert "fullText" in response.json()["data"]["case"]

def test_structure_case_empty_free_text():
    response = client.post(
        "/api/cases/structuring",
        json={"freeText": ""}
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "freeText는 비어 있을 수 없습니다."

def test_structure_case_missing_free_text():
    response = client.post(
        "/api/cases/structuring",
        json={}
    )
    assert response.status_code == 400  # Changed from 422 to 400
    assert response.json()["error"]["message"] == "요청 파라미터가 잘못되었습니다." # This will be the message from validation_exception_handler

def test_structure_case_whitespace_free_text():
    response = client.post(
        "/api/cases/structuring",
        json={"freeText": "   "}
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "freeText는 비어 있을 수 없습니다."