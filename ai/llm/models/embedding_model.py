from typing import List
import torch
from utils.logger import setup_logger, get_logger
from sentence_transformers import SentenceTransformer

setup_logger()
logger = get_logger(__name__)

class EmbeddingModel:
    def __init__(self, model_name: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"):
        self.model_name = model_name
        self._model = None
        self._load_model()

    def _load_model(self):
        if self._model is None:
            logger.info(f"SentenceTransformer 모델 로드 중: {self.model_name} (device=cpu)")
            self._model = SentenceTransformer(self.model_name, device="cpu")
            logger.info("SentenceTransformer 모델 로드 완료.")

    def get_embedding(self, text: str) -> List[float]:
        logger.debug(f"텍스트 인코딩 시도: 타입={type(text)}, 값 일부={text[:100]}...")
        embedding = self._model.encode(text, batch_size=1, convert_to_numpy=True)
        return embedding.tolist()

if __name__ == '__main__':
    logger.info("EmbeddingModel 간단 테스트 실행 중...")
    model_instance = EmbeddingModel()
    logger.info(f"로드된 모델: {model_instance.model_name}")

    sample_text = "이것은 예시 문장입니다."
    embedding = model_instance.get_embedding(sample_text)

    logger.info(f"텍스트 '{sample_text}' 임베딩 일부: {embedding[:5]}...")
    logger.info(f"임베딩 차원: {len(embedding)}")
    logger.info("테스트 완료.")
