from fastapi import Depends, Header
from typing import Optional

from core.container import inject
from services.case_analysis_service import CaseAnalysisService
from services.structuring_service import StructuringService
from services.search_service import SearchService
from services.chat_service import ChatService
from services.consultation_service import ConsultationService
from app.api.exceptions import UnauthorizedException

# 의존성 주입을 통한 서비스 생성 함수들
def get_case_analysis_service() -> CaseAnalysisService:
    """CaseAnalysisService 인스턴스를 반환합니다."""
    return inject(CaseAnalysisService)


def get_structuring_service() -> StructuringService:
    """StructuringService 인스턴스를 반환합니다."""
    return inject(StructuringService)


def get_search_service() -> SearchService:
    """SearchService 인스턴스를 반환합니다."""
    return inject(SearchService)


def get_chat_service() -> ChatService:
    """ChatService 인스턴스를 반환합니다."""
    return inject(ChatService)


def get_consultation_service() -> ConsultationService:
    """ConsultationService 인스턴스를 반환합니다."""
    return inject(ConsultationService)

def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """인증 헤더를 확인하고 사용자 정보를 반환합니다."""
    # if authorization is None:
    #     raise UnauthorizedException("인증 헤더가 없습니다.")
    # 실제로는 토큰을 검증하고 사용자 정보를 반환해야 합니다.
    # 여기서는 예시로 "user"를 반환합니다.
    return "user"
