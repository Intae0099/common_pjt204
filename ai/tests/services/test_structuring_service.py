import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable

from services.structuring_service import StructuringService


class MockLLM(Runnable):
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
    
    def invoke(self, input, config=None):
        raise NotImplementedError("Sync invoke not implemented")
    
    async def ainvoke(self, input, config=None):
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            if isinstance(response, Exception):
                raise response
            return AIMessage(content=response)
        return AIMessage(content='{"title": "Default", "summary": "Default", "fullText": "Default"}')


@pytest.fixture
def mock_llm():
    return MockLLM([])


@pytest.fixture
def structuring_service(mock_llm):
    return StructuringService(mock_llm)


@pytest.mark.asyncio
async def test_사건_구조화_정상_처리():
    """자유 형식 텍스트를 구조화된 형식으로 변환하는지 테스트"""
    valid_json_response = """
    {
        "title": "교통사고 손해배상 청구",
        "summary": "교차로에서 발생한 교통사고로 인한 손해배상 분쟁",
        "fullText": "2023년 3월 15일 오후 2시경 서울시 강남구 교차로에서..."
    }
    """
    
    mock_llm = MockLLM([valid_json_response])
    service = StructuringService(mock_llm)
    
    free_text = "교통사고가 났는데 상대방이 보상을 안해줘요"
    result = await service.structure_case(free_text)
    
    assert result["title"] == "교통사고 손해배상 청구"
    assert result["summary"] == "교차로에서 발생한 교통사고로 인한 손해배상 분쟁"
    assert "교차로" in result["fullText"]


@pytest.mark.asyncio
async def test_잘못된_JSON_응답_처리():
    """LLM이 잘못된 JSON을 반환할 때 파싱 로직이 동작하는지 테스트"""
    invalid_json = "이것은 유효하지 않은 JSON입니다"
    
    mock_llm = MockLLM([invalid_json])
    service = StructuringService(mock_llm)
    
    result = await service.structure_case("계약 분쟁 상담")
    
    # 파싱에 실패하더라도 기본값들이 반환되어야 함
    assert "title" in result
    assert "summary" in result
    assert "fullText" in result


@pytest.mark.asyncio
async def test_LLM_예외_발생시_재시도():
    """LLM 호출 중 예외가 발생했을 때 재시도 로직이 동작하는지 테스트"""
    success_response = """
    {
        "title": "재시도 성공",
        "summary": "첫 번째 시도는 실패했지만 두 번째 시도에서 성공",
        "fullText": "재시도 메커니즘이 정상적으로 동작함"
    }
    """
    
    # 첫 번째 호출은 예외, 두 번째 호출은 성공
    mock_llm = MockLLM([Exception("첫 번째 시도 실패"), success_response])
    service = StructuringService(mock_llm)
    
    result = await service.structure_case("분쟁 사건")
    
    assert result["title"] == "재시도 성공"
    assert mock_llm.call_count == 2


@pytest.mark.asyncio
async def test_최대_재시도_횟수_초과시_예외_발생():
    """최대 재시도 횟수를 초과하면 예외가 발생하는지 테스트"""
    # 모든 시도에서 예외 발생
    mock_llm = MockLLM([
        Exception("첫 번째 실패"),
        Exception("두 번째 실패"), 
        Exception("세 번째 실패")
    ])
    service = StructuringService(mock_llm)
    
    with pytest.raises(Exception):
        await service.structure_case("분쟁 사건")


@pytest.mark.asyncio
async def test_빈_텍스트_처리():
    """빈 텍스트가 입력되어도 정상적으로 처리하는지 테스트"""
    response = """
    {
        "title": "내용 없음",
        "summary": "제공된 텍스트가 없음",
        "fullText": "구조화할 내용이 없습니다"
    }
    """
    
    mock_llm = MockLLM([response])
    service = StructuringService(mock_llm)
    
    result = await service.structure_case("")
    
    assert "title" in result
    assert "summary" in result
    assert "fullText" in result