
from pydantic import BaseModel, Field


class StructuringRequest(BaseModel):
    freeText: str = Field(..., description="자유 서술 형태의 사건 개요")


class CasePayload(BaseModel):
    title: str = Field(..., description="사건 개요의 제목")
    summary: str = Field(..., description="사건 개요의 요약")
    fullText: str = Field(..., description="사건 개요의 전체 본문")


from typing import Dict
from app.api.schemas.analysis import CaseInput

class CaseData(BaseModel):
    case: CaseInput = Field(..., description="사건 정보")

class StructuringResponse(BaseModel):
    success: bool = Field(..., description="요청 처리 성공 여부")
    data: CaseData = Field(..., description="처리 결과 데이터")
