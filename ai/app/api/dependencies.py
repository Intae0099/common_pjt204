from fastapi import Depends
from langchain.llms.base import LLM
from ai.llm import Gpt4oMini # 실제 LLM 구현체
from ai.services.case_analysis_service import CaseAnalysisService

def get_llm() -> LLM:
    """LLM 인스턴스를 반환합니다."""
    return Gpt4oMini()

def get_case_analysis_service(llm: LLM = Depends(get_llm)) -> CaseAnalysisService:
    """CaseAnalysisService 인스턴스를 반환합니다."""
    return CaseAnalysisService(llm)