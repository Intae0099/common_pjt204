import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from services.structuring_service import StructuringService

class MockLLM(Runnable):
    def __init__(self, responses, raise_exception_on_call=None):
        self.responses = responses
        self.call_count = 0
        self.raise_exception_on_call = raise_exception_on_call

    def invoke(self, input: dict, config=None) -> AIMessage:
        # This method is not used in the async tests, but required by Runnable ABC
        raise NotImplementedError("Sync invoke not implemented for MockLLM")

    async def ainvoke(self, input: dict, config=None) -> AIMessage:
        if self.raise_exception_on_call and self.call_count + 1 == self.raise_exception_on_call:
            self.call_count += 1
            raise Exception("Simulated LLM error")
        
        if self.call_count < len(self.responses):
            response_content = self.responses[self.call_count]
            self.call_count += 1
            return AIMessage(content=response_content)
        else:
            # Fallback for more calls than responses, or if no responses are provided
            self.call_count += 1
            return AIMessage(content=json.dumps({"title": "Default Title", "summary": "Default Summary", "fullText": "Default Full Text"}))

@pytest.mark.asyncio
async def test_structure_case_success():
    mock_response = {
        "title": "Test Title",
        "summary": "Test Summary",
        "fullText": "Test Full Text"
    }
    mock_llm = MockLLM(responses=[json.dumps(mock_response)])
    service = StructuringService(llm=mock_llm)
    
    free_text = "This is a test free text."
    result = await service.structure_case(free_text)
    
    assert result == mock_response
    assert mock_llm.call_count == 1

@pytest.mark.asyncio
async def test_structure_case_retry_on_json_error():
    invalid_json_response = "{'title': 'Invalid JSON'"
    valid_json_response = {
        "title": "Valid Title",
        "summary": "Valid Summary",
        "fullText": "Valid Full Text"
    }
    mock_llm = MockLLM(responses=[invalid_json_response, json.dumps(valid_json_response)])
    service = StructuringService(llm=mock_llm)
    
    free_text = "This is a test free text."
    result = await service.structure_case(free_text)
    
    assert result == valid_json_response
    assert mock_llm.call_count == 2

@pytest.mark.asyncio
async def test_structure_case_retry_on_validation_error():
    invalid_structure_response = json.dumps({"title": "Only Title"})
    valid_json_response = {
        "title": "Valid Title",
        "summary": "Valid Summary",
        "fullText": "Valid Full Text"
    }
    mock_llm = MockLLM(responses=[invalid_structure_response, json.dumps(valid_json_response)])
    service = StructuringService(llm=mock_llm)
    
    free_text = "This is a test free text."
    result = await service.structure_case(free_text)
    
    assert result == valid_json_response
    assert mock_llm.call_count == 2

@pytest.mark.asyncio
async def test_structure_case_max_retries_exceeded():
    invalid_json_response = "{'title': 'Invalid JSON'"
    mock_llm = MockLLM(responses=[invalid_json_response] * 5)
    service = StructuringService(llm=mock_llm)
    
    free_text = "This is a test free text."
    with pytest.raises(RuntimeError, match="사건 구조화에 여러 번 재시도한 후에도 실패했습니다."):
        await service.structure_case(free_text)
    
    assert mock_llm.call_count == 3

@pytest.mark.asyncio
async def test_structure_case_early_exit_on_success():
    mock_response = {
        "title": "Early Exit Title",
        "summary": "Early Exit Summary",
        "fullText": "Early Exit Full Text"
    }
    mock_llm = MockLLM(responses=[json.dumps(mock_response), "Should not be called"])
    service = StructuringService(llm=mock_llm)
    
    free_text = "This is a test free text."
    result = await service.structure_case(free_text)
    
    assert result == mock_response
    assert mock_llm.call_count == 1

@pytest.mark.asyncio
async def test_structure_case_llm_exception_retry():
    mock_response = {
        "title": "Success Title",
        "summary": "Success Summary",
        "fullText": "Success Full Text"
    }
    # Simulate an exception on the first call, then success
    mock_llm = MockLLM(responses=["dummy_response_for_failed_attempt", json.dumps(mock_response)], raise_exception_on_call=1)
    service = StructuringService(llm=mock_llm)

    free_text = "Text that causes an LLM error initially."
    result = await service.structure_case(free_text)

    assert result == mock_response
    assert mock_llm.call_count == 2 # First call fails, second call succeeds
