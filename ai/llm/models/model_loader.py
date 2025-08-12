from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel
from utils.logger import get_logger

logger = get_logger(__name__)

class ModelLoader:
    _embedding_model_instance: EmbeddingModel = None
    _cross_encoder_model_instance: CrossEncoderModel = None

    @classmethod
    def get_embedding_model(cls) -> EmbeddingModel:
        if cls._embedding_model_instance is None:
            logger.info("Initializing Embedding Model via ModelLoader.")
            cls._embedding_model_instance = EmbeddingModel()
        return cls._embedding_model_instance

    @classmethod
    def get_cross_encoder_model(cls) -> CrossEncoderModel:
        if cls._cross_encoder_model_instance is None:
            logger.info("Initializing Cross-Encoder Model via ModelLoader.")
            cls._cross_encoder_model_instance = CrossEncoderModel()
        return cls._cross_encoder_model_instance
