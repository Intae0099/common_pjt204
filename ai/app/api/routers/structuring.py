from fastapi import APIRouter, HTTPException, Request, Depends
from app.api.schemas.structuring import StructuringRequest, StructuringResponse, CasePayload
from app.api.decorators import handle_api_exceptions
from app.api.response_models import BaseResponse
from utils.logger import get_logger
from services.structuring_service import StructuringService
from app.api.dependencies import get_structuring_service

router = APIRouter()
logger = get_logger(__name__)

@router.post(
    "/cases/structuring",
    response_model=BaseResponse[dict],
    summary="사건 개요 표준 구조 변환",
    description="자유 서술 형태의 사건 개요를 표준 구조(제목/요약/전체 본문)로 변환합니다."
)
@handle_api_exceptions("사건 구조화가 성공적으로 완료되었습니다.")
async def structure_case(
    structuring_request: StructuringRequest,
    structuring_service: StructuringService = Depends(get_structuring_service)
):
    logger.info(f"[Request Received] POST /cases/structuring - freeText: {structuring_request.freeText[:50]}...")

    if not structuring_request.freeText or structuring_request.freeText.strip() == "":
        logger.warning("[Validation Error] freeText is missing or empty.")
        raise HTTPException(status_code=400, detail="freeText는 비어 있을 수 없습니다.")

    # 예외 처리는 데코레이터가 담당
    structured_case_data = await structuring_service.structure_case(structuring_request.freeText)
    structured_case = CasePayload(**structured_case_data)
    
    response_data = {"case": structured_case.model_dump()}
    logger.info("[Response Sent] POST /cases/structuring - Success")
    
    return response_data
