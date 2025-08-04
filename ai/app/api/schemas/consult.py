from pydantic import BaseModel
from typing import List

class CaseInfo(BaseModel):
    """사건 경위서 정보를 담는 모델"""
    title: str
    summary: str
    fullText: str

class ConsultationRequest(BaseModel):
    """상담 신청서 생성 요청 모델"""
    case: CaseInfo
    desiredOutcome: str
    weakPoints: str

class ApplicationCase(BaseModel):
    """응답 데이터 내 사건 정보 모델"""
    title: str
    summary: str
    fullText: str

class ApplicationData(BaseModel):
    """응답 데이터 내 신청서 객체 모델"""
    case: ApplicationCase
    weakPoints: str
    desiredOutcome: str

class ConsultationData(BaseModel):
    """최종 응답의 데이터 필드 모델"""
    application: ApplicationData
    questions: List[str]
    tags: List[str]

class ConsultationResponse(BaseModel):
    """상담 신청서 생성 최종 응답 모델"""
    success: bool
    data: ConsultationData
