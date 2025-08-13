"""
의존성 주입 컨테이너
"""
from typing import Dict, Type, TypeVar, Callable, Any, Optional
from abc import ABC, abstractmethod

from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel
from llm.models.model_loader import ModelLoader
from services.search_service import SearchService
from services.structuring_service import StructuringService
from services.case_analysis_service import CaseAnalysisService
from services.chat_service import ChatService
from services.consultation_service import ConsultationService
from llm.clients.openai_client import get_async_openai_client
from llm.clients.langchain_client import Gpt4oMini

T = TypeVar('T')


class Container:
    """간단한 의존성 주입 컨테이너"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        
    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """싱글톤 인스턴스 등록"""
        key = interface.__name__
        self._singletons[key] = instance
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """팩토리 함수 등록"""
        key = interface.__name__
        self._factories[key] = factory
    
    def get(self, interface: Type[T]) -> T:
        """의존성 조회"""
        key = interface.__name__
        
        # 싱글톤 먼저 확인
        if key in self._singletons:
            return self._singletons[key]
        
        # 팩토리 확인
        if key in self._factories:
            instance = self._factories[key]()
            return instance
        
        # 등록되지 않은 경우 기본 생성
        try:
            return interface()
        except TypeError as e:
            raise ValueError(f"Cannot create instance of {interface.__name__}: {e}")
    
    def setup_default_dependencies(self):
        """기본 의존성들을 설정"""
        # 모델들 (싱글톤)
        embedding_model = ModelLoader.get_embedding_model()
        cross_encoder_model = ModelLoader.get_cross_encoder_model()
        
        self.register_singleton(EmbeddingModel, embedding_model)
        self.register_singleton(CrossEncoderModel, cross_encoder_model)
        
        # LLM 클라이언트들
        self.register_factory(
            Gpt4oMini,
            lambda: Gpt4oMini()
        )
        
        # OpenAI 클라이언트 (import 추가 필요)
        from llm.clients.openai_client import get_async_openai_client
        self.register_factory(
            type(get_async_openai_client()),
            get_async_openai_client
        )
        
        # 서비스들 (매번 새 인스턴스)
        self.register_factory(
            SearchService,
            lambda: SearchService(
                self.get(EmbeddingModel),
                self.get(CrossEncoderModel)
            )
        )
        
        self.register_factory(
            StructuringService,
            lambda: StructuringService(self.get(Gpt4oMini))
        )
        
        self.register_factory(
            CaseAnalysisService,
            lambda: CaseAnalysisService(
                self.get(Gpt4oMini),
                self.get(SearchService)
            )
        )
        
        self.register_factory(
            ChatService,
            lambda: ChatService(get_async_openai_client())
        )
        
        self.register_factory(
            ConsultationService,
            lambda: ConsultationService(get_async_openai_client())
        )


# 전역 컨테이너 인스턴스
_container: Optional[Container] = None


def get_container() -> Container:
    """컨테이너 인스턴스 반환 (싱글톤)"""
    global _container
    if _container is None:
        _container = Container()
        _container.setup_default_dependencies()
    return _container


def inject(interface: Type[T]) -> T:
    """의존성 주입 헬퍼 함수"""
    return get_container().get(interface)