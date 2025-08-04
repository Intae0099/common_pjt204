from fastapi import APIRouter, Depends
from app.api.schemas.consult import ConsultationRequest, ConsultationResponse
from services.consultation_service import ConsultationService
from app.api.dependencies import get_consultation_service

router = APIRouter()

@router.post("/consult", response_model=ConsultationResponse)
async def create_consultation_application(
    request: ConsultationRequest,
    service: ConsultationService = Depends(get_consultation_service)
):
    """
    상담 신청서와 핵심 질문을 생성하고 저장합니다.
    """
    result_data = await service.create_application_and_questions(request)
    
    return ConsultationResponse(
        success=True,
        data=result_data
    )
