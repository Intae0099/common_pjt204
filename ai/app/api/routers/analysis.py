# app/api/routers/analysis.py
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_case_analysis_service, get_current_user
from app.api.dependencies_queue import get_queue_service
from app.api.exceptions import BadRequestException
from app.api.schemas.analysis import (
    AnalysisRequest, AnalysisResponseData, AnalysisResponse
)
from app.api.schemas.error import BaseErrorResponse
from services.case_analysis_service import CaseAnalysisService
from services.lightweight_queue_manager import LightweightQueueManager, ResourceExhaustionError, QueueFullError

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
    user_id: str = Depends(get_current_user),
    queue_service: LightweightQueueManager = Depends(get_queue_service),
):
    if not request.case or not getattr(request.case, "fullText", "").strip():
        raise BadRequestException("필수 필드 'case.fullText'가 누락되었습니다.")

    try:
        # 큐를 통한 처리
        request_data = {
            "user_query": request.case.fullText,
            "recommend_lawyers": request.recommend_lawyers
        }
        
        service_result = await queue_service.submit_and_wait(
            service_type="case_analysis",
            request_data=request_data,
            user_id=user_id,
            timeout=300  # 5분 타임아웃
        )
        
        if not service_result:
            raise BadRequestException("분석 서비스에서 결과를 반환하지 않았습니다.")
        
        case_analysis_report = service_result.get("case_analysis")
        
        if not case_analysis_report:
            raise BadRequestException("사건 분석 결과를 생성하지 못했습니다.")

        data = AnalysisResponseData(
            report=case_analysis_report
        )
        # 공통 응답 규격으로 반환
        return {"success": True, "data": data}
        
    except QueueFullError:
        raise BadRequestException("현재 요청이 많아 처리할 수 없습니다. 잠시 후 다시 시도해주세요.")
    except ResourceExhaustionError:
        raise BadRequestException("시스템 리소스가 부족합니다. 잠시 후 다시 시도해주세요.")
    except Exception as e:
        raise BadRequestException(f"분석 처리 중 오류가 발생했습니다: {str(e)}")


