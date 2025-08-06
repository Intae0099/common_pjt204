import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.runnables import Runnable

from services.case_analysis_service import CaseAnalysisService
from services.search_service import SearchService


class MockChain(Runnable):
    def __init__(self, response):
        self.response = response
    
    def invoke(self, input):
        return {"text": self.response}


@pytest.fixture
def mock_search_service():
    search_service = MagicMock(spec=SearchService)
    search_service.vector_search = AsyncMock(return_value=(
        [
            {"case_id": "2020다123", "issue": "손해배상", "chunk_text": "계약 위반 시 손해배상 의무"},
            {"case_id": "2021다456", "issue": "계약해지", "chunk_text": "중대한 사유로 인한 계약해지"}
        ], 
        2
    ))
    return search_service


@pytest.fixture
def mock_llm():
    return MagicMock()


@pytest.fixture
def case_analysis_service(mock_llm, mock_search_service):
    service = CaseAnalysisService(mock_llm, mock_search_service)
    return service


@pytest.mark.asyncio
async def test_벡터_검색_및_판례_조회_성공(case_analysis_service, mock_search_service):
    """벡터 검색을 통해 관련 판례를 정상적으로 조회하는지 테스트"""
    mock_chain_response = """
    {
        "data": {
            "report": {
                "issues": ["계약위반", "손해배상"],
                "opinion": "계약위반 시 손해배상이 가능합니다",
                "sentencePrediction": "민사소송",
                "confidence": 0.85,
                "references": {"cases": ["2020다123"], "statutes": ["민법 제390조"]}
            }
        },
        "tags": ["민사", "계약"],
        "recommendedLawyers": []
    }
    """
    case_analysis_service.chain = MockChain(mock_chain_response)
    
    result = await case_analysis_service.analyze_case("계약 위반 시 손해배상 청구 가능한가요?", 2)
    
    mock_search_service.vector_search.assert_called_once_with("계약 위반 시 손해배상 청구 가능한가요?", size=2)
    assert "case_analysis" in result


@pytest.mark.asyncio 
async def test_법률_분석_결과_파싱_성공(case_analysis_service):
    """LLM 응답을 정상적으로 파싱하여 분석 결과를 반환하는지 테스트"""
    valid_response = """
    {
        "data": {
            "report": {
                "issues": ["손해배상"],
                "opinion": "손해배상이 가능합니다",
                "sentencePrediction": "승소 예상",
                "confidence": 0.9,
                "references": {"cases": ["2020다123"], "statutes": ["민법 제390조"]}
            }
        },
        "tags": ["민사"],
        "recommendedLawyers": [{"id": 1, "name": "김변호사", "matchScore": 0.8}]
    }
    """
    case_analysis_service.chain = MockChain(valid_response)
    
    result = await case_analysis_service.analyze_case("손해배상 문의", 1)
    
    assert result["case_analysis"].issues == ["손해배상"]
    assert result["case_analysis"].opinion == "손해배상이 가능합니다"
    assert result["case_analysis"].confidence == 0.9


@pytest.mark.asyncio
async def test_검색된_판례가_없을_때_처리(case_analysis_service, mock_search_service):
    """검색 결과가 없을 때도 정상적으로 분석을 진행하는지 테스트"""
    mock_search_service.vector_search = AsyncMock(return_value=([], 0))
    
    mock_response = """
    {
        "data": {
            "report": {
                "issues": ["일반상담"],
                "opinion": "관련 판례가 없어도 일반적인 법률 조언 가능",
                "sentencePrediction": "해당없음",
                "confidence": 0.5,
                "references": {"cases": [], "statutes": []}
            }
        },
        "tags": ["일반"],
        "recommendedLawyers": []
    }
    """
    case_analysis_service.chain = MockChain(mock_response)
    
    result = await case_analysis_service.analyze_case("특이한 법률 문의", 1)
    
    assert result["case_analysis"].issues == ["일반상담"]
    assert result["case_analysis"].confidence == 0.5