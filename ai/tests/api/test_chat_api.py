import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.api.dependencies import get_current_user

# TestClient fixture
@pytest.fixture(name="client")
def client_fixture():
    """FastAPI TestClient fixture."""
    # Mock dependency for all tests in this module
    app.dependency_overrides[get_current_user] = lambda: "test_user"
    yield TestClient(app)
    # Clean up dependency override after tests
    app.dependency_overrides = {}

# [AI-CHAT-09] Test for successful streaming and memory context
def test_successful_streaming_and_memory(client: TestClient):
    """
    Tests if the chat stream works correctly and maintains conversation history.
    1. Sends a first message to establish context.
    2. Sends a second message that refers to the first one.
    3. Verifies that the context from the first message is included in the LLM call for the second message.
    """
    # Mock the LLM client
    with patch("services.chat_service.call_gpt4o") as mock_call_gpt4o:
        # 1. First call: Establish context
        first_message = "안녕, 내 이름은 제미니야."
        
        # Mock LLM stream response for the first call
        mock_stream_1 = MagicMock()
        mock_stream_1.__iter__.return_value = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="안녕하세요!"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" 반갑습니다."))]),
        ]
        mock_call_gpt4o.return_value = mock_stream_1

        response1 = client.post("/api/ai/chat/stream", json={"message": first_message})
        
        # Verify the first response
        assert response1.status_code == 200
        assert "data: {\"reply\":\"안녕하세요!\"}" in response1.text
        assert "data: {\"reply\":\" 반갑습니다.\"}" in response1.text
        assert "data: [DONE]" in response1.text

        # 2. Second call: Refer to the context
        second_message = "내 이름이 뭐라고 했지?"

        # Mock LLM stream response for the second call
        mock_stream_2 = MagicMock()
        mock_stream_2.__iter__.return_value = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="당신의 이름은"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" '제미니'입니다."))]),
        ]
        mock_call_gpt4o.return_value = mock_stream_2
        
        response2 = client.post("/api/ai/chat/stream", json={"message": second_message})

        # Verify the second response
        assert response2.status_code == 200
        assert "data: {\"reply\":\"당신의 이름은\"}" in response2.text
        assert "data: {\"reply\":\" '제미니'입니다.\"}" in response2.text
        assert "data: [DONE]" in response2.text

        # 3. Verify memory: Check arguments of the second LLM call
        # The call_args[0][0] accesses the first positional argument ('messages') of the call.
        called_messages = mock_call_gpt4o.call_args[0][0]
        
        expected_history = [
            {"role": "user", "content": "안녕, 내 이름은 제미니야."},
            {"role": "assistant", "content": "안녕하세요! 반갑습니다."},
            {"role": "user", "content": "내 이름이 뭐라고 했지?"},
        ]
        
        assert called_messages == expected_history

# [AI-CHAT-10] Test for exception handling during streaming
def test_streaming_exception_handling(client: TestClient):
    """
    Tests if the server handles exceptions gracefully during an LLM stream.
    - Mocks the LLM client to raise an exception mid-stream.
    - Mocks the logger to verify that the error is logged.
    - Checks that the stream is terminated correctly with a [DONE] message.
    """
    # Mock the logger to capture error messages
    with patch("services.chat_service.logger.error") as mock_logger_error:
        # Mock the LLM client to raise an exception
        with patch("services.chat_service.call_gpt4o") as mock_call_gpt4o:
            
            def stream_generator_with_exception():
                yield MagicMock(choices=[MagicMock(delta=MagicMock(content="첫 번째 청크..."))])
                raise Exception("Test LLM Error")

            mock_call_gpt4o.return_value = stream_generator_with_exception()

            response = client.post("/api/ai/chat/stream", json={"message": "이 요청은 실패할 것입니다."})

            # Verify the response
            assert response.status_code == 200
            # The client should receive the first chunk and then the DONE signal
            assert "data: {\"reply\":\"첫 번째 청크...\"}" in response.text
            assert "data: [DONE]" in response.text
            
            # Verify that the error was logged
            mock_logger_error.assert_called_once()
            # Check if the log message contains the expected error text
            assert "Test LLM Error" in mock_logger_error.call_args[0][0]