import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user

# Assuming a simple mock for get_current_user for testing purposes
# In a real scenario, you might mock the actual dependency or use a test user
@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)


def test_chat_stream_success(client: TestClient):
    # Mock authentication for testing
    app.dependency_overrides[get_current_user] = lambda: "test_user"

    response = client.post(
        "/api/ai/chat/stream",
        json={
            "message": "Hello, AI!"
        },
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    import json

    received_data = []
    for line in response.iter_lines():
        if line.startswith("data:"):
            data_str = line[len("data:"):].strip()
            if data_str == "[DONE]":
                received_data.append("[DONE]")
            else:
                received_data.append(json.loads(data_str))

    # Check for expected chunks and the DONE signal
    assert {"reply": "Hello"} in received_data
    assert {"reply": ", "} in received_data
    assert {"reply": "world"} in received_data
    assert {"reply": "!"} in received_data
    assert "[DONE]" in received_data

    # Clean up dependency override
    app.dependency_overrides = {}


def test_chat_stream_validation_failure(client: TestClient):
    # Mock authentication for testing
    app.dependency_overrides[get_current_user] = lambda: "test_user"

    response = client.post(
        "/api/ai/chat/stream",
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "error": {"code": "INVALID_PARAM", "message": "요청 파라미터가 잘못되었습니다."},
        "details": [
            {
                "type": "missing",
                "loc": ["body", "message"],
                "msg": "Field required",
                "input": {},
            }
        ],
    }

    # Clean up dependency override
    app.dependency_overrides = {}
