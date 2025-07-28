from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.api.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.api.dependencies import get_case_analysis_service
from services.case_analysis_service import CaseAnalysisService

router = APIRouter()

@router.post("/analysis", response_model=AnalysisResponse)
async def analyze_case_endpoint(
    request: AnalysisRequest,
    case_analysis_service: CaseAnalysisService = Depends(get_case_analysis_service)
):
    try:
        result = case_analysis_service.analyze_case(request.query)
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
