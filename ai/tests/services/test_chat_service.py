import pytest
import json
from unittest.mock import AsyncMock
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta
from app.api.schemas.chat import ChatRequest
from services.chat_service import ChatService

@pytest.fixture
def mock_async_openai_client():
    """비동기 OpenAI 클라이언트의 모의 객체를 생성합니다."""
    mock_client = AsyncMock()
    
    async def mock_stream_generator(*args, **kwargs):
        chunks = [
            ChatCompletionChunk(
                id='chatcmpl-test', 
                choices=[Choice(delta=ChoiceDelta(content='Hello'), finish_reason=None, index=0)], 
                created=1677652288, model='gpt-4o-mini', object='chat.completion.chunk', system_fingerprint=None
            ),
            ChatCompletionChunk(
                id='chatcmpl-test', 
                choices=[Choice(delta=ChoiceDelta(content=' world'), finish_reason=None, index=0)], 
                created=1677652288, model='gpt-4o-mini', object='chat.completion.chunk', system_fingerprint=None
            ),
        ]
        for chunk in chunks:
            yield chunk

    # create를 호출할 때마다 새로운 generator를 반환하도록 side_effect를 사용합니다.
    mock_client.chat.completions.create.side_effect = mock_stream_generator
    return mock_client

@pytest.mark.asyncio
async def test_stream_chat_response_generator(mock_async_openai_client):
    """스트리밍 응답이 올바르게 생성되는지 테스트합니다."""
    service = ChatService(mock_async_openai_client)
    req = ChatRequest(message="Hello")
    user_id = "test_user"

    chunks = [chunk async for chunk in service.stream_chat_response(req, user_id)]
    
    assert len(chunks) == 3 # Hello, world, [DONE]
    
    # 첫 번째 청크의 JSON을 파싱하여 reply 값을 확인
    chunk1_data = json.loads(chunks[0].replace("data: ", ""))
    assert chunk1_data['reply'] == "Hello"

    # 두 번째 청크의 JSON을 파싱하여 reply 값을 확인
    chunk2_data = json.loads(chunks[1].replace("data: ", ""))
    assert chunk2_data['reply'] == " world"
    
    assert chunks[2] == "data: [DONE]\n\n"

@pytest.mark.asyncio
async def test_prompt_generation_with_history(mock_async_openai_client):
    """채팅 기록이 프롬프트에 올바르게 포함되는지 테스트합니다."""
    service = ChatService(mock_async_openai_client)
    user_id = "test_user_2"
    
    # 첫 번째 요청
    req1 = ChatRequest(message="My name is John.")
    _ = [chunk async for chunk in service.stream_chat_response(req1, user_id)]

    # 두 번째 요청
    req2 = ChatRequest(message="What is my name?")
    _ = [chunk async for chunk in service.stream_chat_response(req2, user_id)]

    # `create`가 두 번째로 호출될 때의 `messages` 인수를 확인
    call_args = mock_async_openai_client.chat.completions.create.call_args
    messages = call_args.kwargs['messages']
    
    assert len(messages) == 4 # System, User, Assistant, User
    assert messages[1]['role'] == 'user'
    assert messages[1]['content'] == 'My name is John.'
    assert messages[2]['role'] == 'assistant'
    assert messages[2]['content'] == 'Hello world'
    assert messages[3]['role'] == 'user'
    assert messages[3]['content'] == 'What is my name?'

@pytest.mark.asyncio
async def test_chat_history_pruning(mock_async_openai_client):
    """채팅 기록이 최대 토큰을 초과하면 가장 오래된 기록이 삭제되는지 테스트합니다."""
    service = ChatService(mock_async_openai_client)
    service.MAX_HISTORY_TOKENS = 80 # 테스트를 위해 토큰 제한 낮춤
    user_id = "test_user_3"

    # 기록 쌓기 (user, assistant)
    req1 = ChatRequest(message="This is a long message to fill up the history quickly. First message.")
    _ = [chunk async for chunk in service.stream_chat_response(req1, user_id)]
    
    # 기록 추가 (user, assistant) - 이 대화 쌍이 남아야 함
    req2 = ChatRequest(message="This is the second message, which should remain.")
    _ = [chunk async for chunk in service.stream_chat_response(req2, user_id)]

    # 기록 확인
    history = service.chat_histories[user_id]
    assert len(history) == 2 # (user, assistant) 한 쌍만 남아야 함
    assert history[0][0] == 'user'
    assert history[0][1] == 'This is the second message, which should remain.'
    assert history[1][0] == 'assistant'
    assert history[1][1] == 'Hello world'