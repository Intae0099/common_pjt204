# app/api/schemas/search.py
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

# 1. 목록 검색 (/search/cases)
class CaseSnippet(BaseModel):
    caseId: str = Field(..., description="판례 일련번호")
    title: str = Field(..., description="사건명")
    decisionDate: Optional[date] = Field(None, description="선고일자")
    category: str = Field(..., description="사건 종류 (예: 민사)")
    issue: Optional[str] = Field(None, description="판시사항 일부 (스니펫)")
    summary: Optional[str] = Field(None, description="판시사항 일부 (스니펫)")

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


class CaseDetail(BaseModel):
    caseId: str = Field(..., description="판례 일련번호")
    title: str = Field(..., description="사건명")
    decisionDate: Optional[date] = Field(None, description="선고일자")
    category: str = Field(..., description="사건 종류 (예: 민사)")
    issue: Optional[str] = Field(None, description="판시사항")
    summary: Optional[str] = Field(None, description="요약")
    statutes: str = Field(default="", description="참조 법령 (세미콜론 구분)")
    precedents: str = Field(default="", description="참조 판례 (세미콜론 구분)")
    fullText: str = Field(..., description="판례 전문 원문")

class CaseDetailResponse(BaseModel):
    success: bool
    data: CaseDetail
