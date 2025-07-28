from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from app.api.schemas.analysis import AnalysisRequest, AnalysisResponse, CaseAnalysisResult, AnalysisResponseData
from app.api.dependencies import get_case_analysis_service
from services.case_analysis_service import CaseAnalysisService

router = APIRouter()

@router.post("/analysis", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_case_endpoint(
    request: AnalysisRequest,
    case_analysis_service: CaseAnalysisService = Depends(get_case_analysis_service)
):
    try:
        # case_analysis_service.analyze_case는 { "case_analysis": CaseAnalysisResult 객체 } 형태를 반환
        service_result = case_analysis_service.analyze_case(
            user_query=request.case.fullText, # request.query 대신 request.case.fullText 사용
        )

        # service_result에서 CaseAnalysisResult 객체를 추출
        case_analysis_report = service_result.get("case_analysis")

        # 응답 예시에 맞게 tags와 recommendedLawyers를 추출 (현재 서비스 로직에 없으므로 빈 리스트로 가정)
        # 실제 서비스 로직에서 이 값들을 반환하도록 수정해야 합니다.
        tags = case_analysis_report.tags if case_analysis_report else []
        recommended_lawyers = case_analysis_report.recommendedLawyers if case_analysis_report else []

        # AnalysisResponseData 객체 생성
        response_data = AnalysisResponseData(
            report=case_analysis_report,
            tags=tags,
            recommendedLawyers=recommended_lawyers
        )

        # 최종 AnalysisResponse 객체 반환
        return AnalysisResponse(success=True, data=response_data)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
