from fastapi import APIRouter, HTTPException, Request, Depends
from app.api.schemas.structuring import StructuringRequest, StructuringResponse, CasePayload
from utils.logger import get_logger
from services.structuring_service import StructuringService
from app.api.dependencies import get_structuring_service

router = APIRouter()
logger = get_logger(__name__)

@router.post(
    "/cases/structuring",
    response_model=StructuringResponse,
    summary="사건 개요 표준 구조 변환",
    description="자유 서술 형태의 사건 개요를 표준 구조(제목/요약/전체 본문)로 변환합니다."
)
async def structure_case(
    request: Request,
    structuring_request: StructuringRequest,
    structuring_service: StructuringService = Depends(get_structuring_service)
):
    logger.info(f"[Request Received] POST /cases/structuring - freeText: {structuring_request.freeText[:50]}...")

    if not structuring_request.freeText or structuring_request.freeText.strip() == "":
        logger.warning("[Validation Error] freeText is missing or empty.")
        raise HTTPException(status_code=400, detail="freeText는 비어 있을 수 없습니다.")

    try:
        structured_case_data = await structuring_service.structure_case(structuring_request.freeText)
        structured_case = CasePayload(**structured_case_data)
    except Exception as e:
        logger.error(f"Error structuring case: {e}")
        raise HTTPException(status_code=500, detail=f"사건 개요 구조화 중 오류 발생: {e}")

    response_data = {"case": structured_case.model_dump()}
    response = StructuringResponse(success=True, data=response_data)

    logger.info("[Response Sent] POST /cases/structuring - Success")
    return response
