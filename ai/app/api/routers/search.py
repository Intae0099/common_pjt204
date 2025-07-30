# app/api/routers/search.py
from fastapi import APIRouter, Query, Path, status, Depends
from datetime import date
from typing import List

from app.api.schemas.search import (
    CaseSearchResponse,
    CaseSearchData,
    CaseSnippet,
    PageMeta,
    CaseDetailResponse,
    CaseDetail,
)
from services.search_service import SearchService
from app.api.dependencies import get_search_service
from app.api.exceptions import ResourceNotFoundException

router = APIRouter()

@router.get(
    "/search/cases",
    response_model=CaseSearchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Search"],
    summary="판례 목록 검색",
    description="키워드를 기반으로 판례 메타데이터 목록을 검색합니다.",
)
async def search_cases_endpoint(
    keyword: str = Query(..., min_length=2, description="검색 키워드 (2자 이상)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 당 결과 수"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    판례 목록 검색 API입니다.
    - **keyword**: 검색어 (필수, 2자 이상)
    - **page**: 페이지 번호 (기본값 1)
    - **size**: 페이지 당 결과 수 (기본값 10, 최대 100)
    """
    search_results, total_count = await search_service.vector_search(keyword, page, size, use_rerank=True)

    items = []
    for result in search_results:
        items.append(CaseSnippet(
            caseId=result["case_id"],
            title=result["title"],
            decisionDate=result["decision_date"],
            category=result["category"],
            issue=result["issue"],
            summary=result["summary"] if result["summary"] else result["full_text"][:200] + "..."
        ))

    page_meta = PageMeta(
        total=total_count,
        page=page,
        size=size,
        hasNext=(page * size) < total_count
    )
    dummy_data = CaseSearchData(items=items, pageMeta=page_meta)

    return CaseSearchResponse(success=True, data=dummy_data)


@router.get(
    "/cases/{precId}",
    response_model=CaseDetailResponse,
    status_code=status.HTTP_200_OK,
    tags=["Search"],
    summary="판례 전문 조회",
    description="판례일련번호로 전문과 참조 법령을 조회합니다.",
)
async def get_case_detail_endpoint(
    precId: str = Path(..., description="판례 ID"), # Changed to str as case_id is TEXT
    search_service: SearchService = Depends(get_search_service)
):
    """
    판례 전문 조회 API입니다.
    - **precId**: 판례 ID (필수)
    """
    case_detail = await search_service.get_case_by_id(prec_id=precId)

    if not case_detail:
        raise ResourceNotFoundException("해당 ID의 판례를 찾을 수 없습니다.")

    detail = CaseDetail(
        caseId=case_detail["case_id"],
        title=case_detail["title"],
        decisionDate=case_detail["decision_date"],
        category=case_detail["category"],
        issue=case_detail["issue"],
        summary=case_detail["summary"],
        statutes=case_detail["statutes"] if case_detail["statutes"] else "",
        precedents=case_detail["precedents"] if case_detail["precedents"] else "",
        fullText=case_detail["full_text"],
    )

    return CaseDetailResponse(success=True, data=detail)
