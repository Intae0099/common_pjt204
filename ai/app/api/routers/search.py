# app/api/routers/search.py
from fastapi import APIRouter, Query, Path, status, Depends
from datetime import date, datetime
from typing import List

from app.api.schemas.search import (
    CaseSearchResponse,
    CaseSearchData,
    CaseSnippet,
    PageMeta,
    CaseDetailResponse,
    CaseDetail,
)
from app.api.decorators import handle_api_exceptions, validate_pagination
from app.api.response_models import PaginatedResponse
from services.search_service import SearchService
from app.api.dependencies import get_search_service
from app.api.exceptions import ResourceNotFoundException

router = APIRouter()

@router.get(
    "/search/cases",
    status_code=status.HTTP_200_OK,
    tags=["Search"],
    summary="판례 목록 검색",
    description="키워드를 기반으로 판례 메타데이터 목록을 검색합니다.",
)
@handle_api_exceptions("판례 검색이 성공적으로 완료되었습니다.")
@validate_pagination(max_size=100)
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
        # decision_date가 date 객체가 아닐 경우 변환
        decision_date = result["decision_date"]
        if decision_date and not isinstance(decision_date, date):
            if hasattr(decision_date, 'date'):
                decision_date = decision_date.date()
            else:
                from datetime import datetime
                if isinstance(decision_date, str):
                    try:
                        decision_date = datetime.strptime(decision_date, "%Y-%m-%d").date()
                    except ValueError:
                        decision_date = None
        
        items.append(CaseSnippet(
            caseId=result["case_id"] or "",
            title=result["title"] or "",
            decisionDate=decision_date,  # None도 허용
            category=result["category"] or "",
            issue=result.get("issue"),
            summary=result["summary"] if result["summary"] else (result["full_text"][:200] + "..." if result["full_text"] else "")
        ))

    response = PaginatedResponse.create(
        data=items,
        total=total_count,
        page=page,
        size=size
    )
    
    # 딕셔너리로 변환하여 반환 (pydantic 모델 직접 반환 시 문제 방지)
    return response.model_dump()


@router.get(
    "/cases/{precId}",
    response_model=CaseDetailResponse,
    status_code=status.HTTP_200_OK,
    tags=["Search"],
    summary="판례 전문 조회",
    description="판례일련번호로 전문과 참조 법령을 조회합니다.",
)
@handle_api_exceptions("판례 상세 정보를 성공적으로 조회했습니다.")
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

    # decision_date 처리
    decision_date = case_detail["decision_date"]
    if decision_date and not isinstance(decision_date, date):
        if hasattr(decision_date, 'date'):
            decision_date = decision_date.date()
        else:
            from datetime import datetime
            if isinstance(decision_date, str):
                try:
                    decision_date = datetime.strptime(decision_date, "%Y-%m-%d").date()
                except ValueError:
                    decision_date = date(1900, 1, 1)
    
    # None 값들을 안전하게 처리
    statutes = case_detail.get("statutes")
    precedents = case_detail.get("precedents")
    
    detail = CaseDetail(
        caseId=case_detail["case_id"] or "",
        title=case_detail["title"] or "",
        decisionDate=decision_date,
        category=case_detail["category"] or "",
        issue=case_detail.get("issue"),
        summary=case_detail.get("summary"),
        statutes=statutes if statutes is not None else "",
        precedents=precedents if precedents is not None else "",
        fullText=case_detail["full_text"] or "",
    )

    response = CaseDetailResponse(success=True, data=detail)
    return response.model_dump()
