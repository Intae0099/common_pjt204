from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel
from llm.models.quantized_embedding_model import QuantizedEmbeddingModel
from llm.models.optimized_cross_encoder_model import OptimizedCrossEncoderModel
from utils.logger import get_logger
import os

logger = get_logger(__name__)

class ModelLoader:
    _embedding_model_instance: EmbeddingModel = None
    _cross_encoder_model_instance: CrossEncoderModel = None
    
    # 최적화 모델 사용 여부 설정 (환경변수로 제어)
    USE_OPTIMIZED_MODELS = os.getenv("USE_OPTIMIZED_MODELS", "true").lower() == "true"

    @classmethod
    def get_embedding_model(cls) -> EmbeddingModel:
        if cls._embedding_model_instance is None:
            if cls.USE_OPTIMIZED_MODELS:
                logger.info("[경량화] Quantized Embedding Model 초기화")
                cls._embedding_model_instance = QuantizedEmbeddingModel(enable_quantization=True)
            else:
                logger.info("Original Embedding Model 초기화")
                cls._embedding_model_instance = EmbeddingModel()
        return cls._embedding_model_instance

    @classmethod
    def get_cross_encoder_model(cls) -> CrossEncoderModel:
        if cls._cross_encoder_model_instance is None:
            if cls.USE_OPTIMIZED_MODELS:
                logger.info("[경량화] Optimized Cross-Encoder Model 초기화")
                cls._cross_encoder_model_instance = OptimizedCrossEncoderModel(enable_quantization=True)
            else:
                logger.info("Original Cross-Encoder Model 초기화")
                cls._cross_encoder_model_instance = CrossEncoderModel()
        return cls._cross_encoder_model_instance

    @classmethod
    def get_model_info(cls) -> dict:
        """현재 로드된 모델 정보 반환"""
        info = {
            "use_optimized_models": cls.USE_OPTIMIZED_MODELS,
            "embedding_model_type": type(cls._embedding_model_instance).__name__ if cls._embedding_model_instance else None,
            "cross_encoder_model_type": type(cls._cross_encoder_model_instance).__name__ if cls._cross_encoder_model_instance else None
        }
        
        # 모델별 상세 정보 추가
        if cls._embedding_model_instance and hasattr(cls._embedding_model_instance, 'get_model_info'):
            info["embedding_model_details"] = cls._embedding_model_instance.get_model_info()
            
        if cls._cross_encoder_model_instance and hasattr(cls._cross_encoder_model_instance, 'get_model_info'):
            info["cross_encoder_model_details"] = cls._cross_encoder_model_instance.get_model_info()
        
        return info

    @classmethod
    def reload_models(cls, use_optimized: bool = None):
        """모델 재로드 (최적화 모드 변경 시 사용)"""
        if use_optimized is not None:
            cls.USE_OPTIMIZED_MODELS = use_optimized
        
        # 기존 인스턴스 초기화
        cls._embedding_model_instance = None
        cls._cross_encoder_model_instance = None
        
        logger.info(f"[경량화] 모델 재로드 준비 완료 (최적화 모드: {cls.USE_OPTIMIZED_MODELS})")
