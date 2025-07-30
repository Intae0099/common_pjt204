# app/api/schemas/search.py
from pydantic import BaseModel, Field
from datetime import date
from typing import List

# 1. 목록 검색 (/search/cases)
class CaseSnippet(BaseModel):
    id: int = Field(..., description="판례 일련번호")
    name: str = Field(..., description="사건명")
    court: str = Field(..., description="법원명")
    decisionDate: date = Field(..., description="선고일자")
    tags: List[str] = Field(default_factory=list, description="사건 관련 태그")
    snippet: str = Field(..., description="판시사항 일부 (스니펫)")

class PageMeta(BaseModel):
    total: int = Field(..., description="전체 검색 결과 수")
    page: int = Field(..., description="현재 페이지 번호")
    size: int = Field(..., description="페이지 당 항목 수")
    hasNext: bool = Field(..., description="다음 페이지 존재 여부")

class CaseSearchData(BaseModel):
    items: List[CaseSnippet]
    pageMeta: PageMeta

class CaseSearchResponse(BaseModel):
    success: bool
    data: CaseSearchData

# 2. 전문 조회 (/cases/{precId})
class ReferenceStatute(BaseModel):
    code: str = Field(..., description="참조 법령명")
    article: str = Field(..., description="참조 조문")

class ReferenceCase(BaseModel):
    id: int = Field(..., description="참조 판례 일련번호")
    name: str = Field(..., description="참조 판례 사건명")
    court: str = Field(..., description="참조 판례 법원명")
    year: int = Field(..., description="참조 판례 선고년도")

class References(BaseModel):
    statutes: List[ReferenceStatute]
    cases: List[ReferenceCase]

class CaseDetail(BaseModel):
    id: int = Field(..., description="판례 일련번호")
    name: str = Field(..., description="사건명")
    court: str = Field(..., description="법원명")
    decisionDate: date = Field(..., description="선고일자")
    caseType: str = Field(..., description="사건 종류 (예: 민사)")
    fullText: str = Field(..., description="판례 전문 원문")
    references: References = Field(..., description="참조 법령 및 판례")

class CaseDetailResponse(BaseModel):
    success: bool
    data: CaseDetail
