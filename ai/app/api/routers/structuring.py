from fastapi import APIRouter, HTTPException, Request
from app.api.schemas.structuring import StructuringRequest, StructuringResponse, CasePayload
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post(
    "/cases/structuring",
    response_model=StructuringResponse,
    summary="사건 개요 표준 구조 변환",
    description="자유 서술 형태의 사건 개요를 표준 구조(제목/요약/전체 본문)로 변환합니다."
)
async def structure_case(request: Request, structuring_request: StructuringRequest):
    logger.info(f"[Request Received] POST /cases/structuring - freeText: {structuring_request.freeText[:50]}...")

    if not structuring_request.freeText or structuring_request.freeText.strip() == "":
        logger.warning("[Validation Error] freeText is missing or empty.")
        raise HTTPException(status_code=400, detail="freeText는 비어 있을 수 없습니다.")

    # TODO: Implement actual structuring logic here
    # For now, return a fake structured case as per requirements
    fake_case = CasePayload(
        title="[Fake] 사건 개요 제목",
        summary="[Fake] 사건 개요 요약입니다. 이 부분은 자유 서술된 내용을 바탕으로 핵심 정보를 간추린 것입니다.",
        fullText=f"[Fake] 사건 개요 전체 본문입니다. 원본 내용: {structuring_request.freeText}"
    )

    response_data = {"case": fake_case.model_dump()}
    response = StructuringResponse(success=True, data=response_data)

    logger.info("[Response Sent] POST /cases/structuring - Success")
    return response
