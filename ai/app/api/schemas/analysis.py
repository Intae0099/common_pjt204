from pydantic import BaseModel
from typing import List, Dict, Any
from ai.llm.llm_response_parser import CaseAnalysisResult

class AnalysisRequest(BaseModel):
    query: str

class AnalysisResponse(BaseModel):
    case_analysis: CaseAnalysisResult
    