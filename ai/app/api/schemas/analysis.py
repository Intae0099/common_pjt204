from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.api.schemas.error import BaseSuccessResponse
from app.api.schemas.statute import StatuteReference

class CaseAnalysisResult(BaseModel):
    issues: List[str] = Field(default_factory=list, description="식별된 주요 법적 쟁점.")
    opinion: str = Field(..., description="분석에 기반한 법적 소견.")
    expected_sentence: str = Field(..., description="예상되는 판결 또는 결과.")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="분석의 신뢰도 점수.")
    references: Dict[str, Any] = Field(default_factory=dict, description="분석에 사용된 참조 자료.")
    statutes: List[StatuteReference] = Field(default_factory=list, description="관련 법령 목록.")
    tags: List[str] = Field(default_factory=list, description="관련 법률 태그.")
    recommendedLawyers: List[Dict[str, Any]] = Field(default_factory=list, description="추천 변호사 목록.")

class CaseInput(BaseModel):
    title: str = Field(..., min_length=1, description="사건 제목.")
    summary: str = Field(..., min_length=1, description="사건 요약.")
    fullText: str = Field(..., min_length=1, description="사건 전체 내용.")

class AnalysisRequest(BaseModel):
    case: CaseInput = Field(..., description="분석할 사건 정보.")
    recommend_lawyers: bool = Field(True, description="변호사 추천 포함 여부.")

class AnalysisResponseData(BaseModel):
    report: CaseAnalysisResult = Field(..., description="상세 법률 분석 결과.")

AnalysisResponse = BaseSuccessResponse[AnalysisResponseData]