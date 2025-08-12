# app/api/routers/analysis.py
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_case_analysis_service, get_current_user
from app.api.exceptions import BadRequestException
from app.api.schemas.analysis import AnalysisRequest, AnalysisResponseData, AnalysisResponse
from app.api.schemas.error import BaseErrorResponse
from services.case_analysis_service import CaseAnalysisService

router = APIRouter()

@router.post(
    "/analysis",
    response_model=AnalysisResponse,               # ← 공통 성공 래퍼 사용
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True,              # ← None 필드 제거
    dependencies=[Depends(get_current_user)],      # ← 인증을 바디 파싱 전에 수행
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse, "description": "잘못된 요청"},
        status.HTTP_401_UNAUTHORIZED: {"model": BaseErrorResponse, "description": "인증 실패"},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse, "description": "리소스를 찾을 수 없음"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": BaseErrorResponse, "description": "서버 내부 오류"},
    },
)
async def analyze_case_endpoint(
    request: AnalysisRequest,
    case_analysis_service: CaseAnalysisService = Depends(get_case_analysis_service),
):
    if not request.case or not getattr(request.case, "fullText", "").strip():
        raise BadRequestException("필수 필드 'case.fullText'가 누락되었습니다.")

    service_result = await case_analysis_service.analyze_case(
        user_query=request.case.fullText,
    )
    case_analysis_report = service_result.get("case_analysis")
    if not case_analysis_report:
        raise BadRequestException("사건 분석 결과를 생성하지 못했습니다.")

    data = AnalysisResponseData(
        report=case_analysis_report,
    )
    # 공통 응답 규격으로 반환
    return {"success": True, "data": data}

