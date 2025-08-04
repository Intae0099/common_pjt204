from fastapi import Depends, Header
from typing import Optional
from llm import Gpt4oMini
from services.case_analysis_service import CaseAnalysisService
from services.structuring_service import StructuringService
from app.api.exceptions import UnauthorizedException
from llm.models.model_loader import ModelLoader
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel

def get_llm() -> Gpt4oMini:
    """LLM 인스턴스를 반환합니다."""
    return Gpt4oMini()

def get_case_analysis_service(
    llm: Gpt4oMini = Depends(get_llm),
    embedding_model: EmbeddingModel = Depends(ModelLoader.get_embedding_model),
    cross_encoder_model: CrossEncoderModel = Depends(ModelLoader.get_cross_encoder_model)
) -> CaseAnalysisService:
    """CaseAnalysisService 인스턴스를 반환합니다."""
    return CaseAnalysisService(llm, embedding_model, cross_encoder_model)

from services.search_service import SearchService
from services.chat_service import ChatService
from services.consultation_service import ConsultationService
from llm.clients.openai_client import async_client as async_openai_client

chat_service_instance = ChatService(async_openai_client)
consultation_service_instance = ConsultationService(async_openai_client)

def get_chat_service() -> ChatService:
    """ChatService 인스턴스를 반환합니다."""
    return chat_service_instance

def get_consultation_service() -> ConsultationService:
    """ConsultationService 인스턴스를 반환합니다."""
    return consultation_service_instance


def get_structuring_service(
    llm: Gpt4oMini = Depends(get_llm)
) -> StructuringService:
    """StructuringService 인스턴스를 반환합니다."""
    return StructuringService(llm)


def get_search_service(
    embedding_model: EmbeddingModel = Depends(ModelLoader.get_embedding_model),
    cross_encoder_model: CrossEncoderModel = Depends(ModelLoader.get_cross_encoder_model)
) -> SearchService:
    """SearchService 인스턴스를 반환합니다."""
    return SearchService(embedding_model, cross_encoder_model)

def get_embedding_model_dependency():
    return ModelLoader.get_embedding_model()

def get_cross_encoder_model_dependency():
    return ModelLoader.get_cross_encoder_model()

def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """인증 헤더를 확인하고 사용자 정보를 반환합니다."""
    # if authorization is None:
    #     raise UnauthorizedException("인증 헤더가 없습니다.")
    # 실제로는 토큰을 검증하고 사용자 정보를 반환해야 합니다.
    # 여기서는 예시로 "user"를 반환합니다.
    return "user"
