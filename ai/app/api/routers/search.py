# app/api/routers/search.py
from fastapi import APIRouter, Query, Path, status
from datetime import date

from app.api.schemas.search import (
    CaseSearchResponse,
    CaseSearchData,
    CaseSnippet,
    PageMeta,
    CaseDetailResponse,
    CaseDetail,
    References,
    ReferenceStatute,
    ReferenceCase,
)

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
    keyword: str = Query(..., min_length=2, description="검색 키워드 (2자 이상)")
):
    """
    임시 데이터로 응답하는 판례 목록 검색 API입니다.
    - **keyword**: 검색어 (필수, 2자 이상)
    """
    # 임시 데이터 생성
    dummy_items = [
        CaseSnippet(
            id=93810,
            name="소유권이전등기말소",
            court="대법원",
            decisionDate=date(1978, 4, 11),
            tags=["민사", "물권"],
            snippet="분배농지 상한선 초과부분에 대한 당연무효 여부...",
        )
    ]
    dummy_page_meta = PageMeta(total=1, page=1, size=10, hasNext=False)
    dummy_data = CaseSearchData(items=dummy_items, pageMeta=dummy_page_meta)

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
    precId: int = Path(..., ge=1, description="대법원 제공 판례일련번호")
):
    """
    임시 데이터로 응답하는 판례 전문 조회 API입니다.
    - **precId**: 판례 일련번호 (필수, 1 이상)
    """
    # 임시 데이터 생성
    dummy_references = References(
        statutes=[ReferenceStatute(code="농지개혁법", article="8조")],
        cases=[
            ReferenceCase(id=12345, name="선행판례", court="대법원", year=1975)
        ],
    )
    dummy_detail = CaseDetail(
        id=precId,
        name="소유권이전등기말소",
        court="대법원",
        decisionDate=date(1978, 4, 11),
        caseType="민사",
        fullText="<판례 전문 원문...>",
        references=dummy_references,
    )

    return CaseDetailResponse(success=True, data=dummy_detail)
