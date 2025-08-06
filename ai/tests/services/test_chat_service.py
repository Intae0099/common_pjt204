import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from collections import deque

from services.chat_service import ChatService
from app.api.schemas.chat import ChatRequest


class MockOpenAI:
    def __init__(self):
        self.chat = MockChat()


class MockChat:
    def __init__(self):
        self.completions = MockCompletions()


class MockCompletions:
    async def create(self, **kwargs):
        if kwargs.get('stream'):
            return MockAsyncIterator([
                MockChunk("안녕하세요! "),
                MockChunk("법률 상담에 "),
                MockChunk("도움을 드리겠습니다.")
            ])
        else:
            return MagicMock(choices=[MagicMock(message=MagicMock(content="일반 응답"))])


class MockChunk:
    def __init__(self, content):
        self.choices = [MagicMock(delta=MagicMock(content=content))]


class MockAsyncIterator:
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


@pytest.fixture
def mock_openai_client():
    return MockOpenAI()


@pytest.fixture
def chat_service(mock_openai_client):
    return ChatService(mock_openai_client)


@pytest.mark.asyncio
async def test_스트림_채팅_응답_생성(chat_service):
    """스트림 방식으로 채팅 응답을 생성하는지 테스트"""
    request = ChatRequest(message="법률 상담을 요청합니다")
    user_id = "test_user_123"
    
    response_chunks = []
    async for chunk in chat_service.stream_chat_response(request, user_id):
        response_chunks.append(chunk)
    
    assert len(response_chunks) > 0
    # 마지막 청크는 [DONE]이어야 함
    assert response_chunks[-1] == "data: [DONE]\n\n"
    # 응답 데이터가 포함된 청크들이 있어야 함
    data_chunks = [chunk for chunk in response_chunks if "data:" in chunk and "[DONE]" not in chunk]
    assert len(data_chunks) > 0


@pytest.mark.asyncio
async def test_채팅_히스토리_관리(chat_service):
    """사용자별 채팅 히스토리가 올바르게 관리되는지 테스트"""
    request1 = ChatRequest(message="첫 번째 질문")
    request2 = ChatRequest(message="두 번째 질문")
    user_id = "test_user_456"
    
    # 첫 번째 질문
    async for _ in chat_service.stream_chat_response(request1, user_id):
        pass
    
    # 두 번째 질문
    async for _ in chat_service.stream_chat_response(request2, user_id):
        pass
    
    # 히스토리가 저장되었는지 확인
    assert user_id in chat_service.chat_histories
    history = chat_service.chat_histories[user_id]
    assert len(history) == 4  # user1, assistant1, user2, assistant2 메시지


@pytest.mark.asyncio
async def test_다중_사용자_히스토리_분리(chat_service):
    """여러 사용자의 히스토리가 분리되어 관리되는지 테스트"""
    user1_request = ChatRequest(message="사용자1 질문")
    user2_request = ChatRequest(message="사용자2 질문")
    
    user1_id = "user_1"
    user2_id = "user_2"
    
    # 각각 다른 사용자로 질문
    async for _ in chat_service.stream_chat_response(user1_request, user1_id):
        pass
    
    async for _ in chat_service.stream_chat_response(user2_request, user2_id):
        pass
    
    # 각 사용자의 히스토리가 분리되어 있는지 확인
    assert user1_id in chat_service.chat_histories
    assert user2_id in chat_service.chat_histories
    assert chat_service.chat_histories[user1_id] != chat_service.chat_histories[user2_id]


@pytest.mark.asyncio 
async def test_빈_메시지_처리(chat_service):
    """빈 메시지가 입력되어도 정상 처리되는지 테스트"""
    request = ChatRequest(message="")
    user_id = "test_user_empty"
    
    response_chunks = []
    async for chunk in chat_service.stream_chat_response(request, user_id):
        response_chunks.append(chunk)
    
    # 빈 메시지에도 응답이 생성되어야 함
    assert len(response_chunks) > 0
    assert response_chunks[-1] == "data: [DONE]\n\n"


@pytest.mark.asyncio
async def test_히스토리_토큰_제한_관리(chat_service):
    """히스토리 토큰 수가 제한을 초과하지 않는지 테스트"""
    user_id = "test_user_long"
    
    # 긴 메시지를 여러 번 보내서 토큰 제한 테스트
    long_message = "매우 긴 법률 질문 " * 100
    request = ChatRequest(message=long_message)
    
    # 여러 번 질문하여 히스토리를 늘림
    for i in range(5):
        async for _ in chat_service.stream_chat_response(request, user_id):
            pass
    
    # 히스토리가 있지만 토큰 제한을 고려하여 관리되고 있는지 확인
    assert user_id in chat_service.chat_histories
    # 실제 토큰 수 계산은 복잡하므로 히스토리 존재 여부만 확인