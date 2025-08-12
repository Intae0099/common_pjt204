from sentence_transformers import CrossEncoder
from functools import lru_cache
import os
from utils.logger import setup_logger, get_logger

logger = get_logger(__name__)

class CrossEncoderModel:
    def __init__(self, model_name: str = "Alibaba-NLP/gte-multilingual-base"):
        self.model_name = model_name
        self._model = None
        self._load_model()

    def _load_model(self):
        if self._model is None:
            logger.info(f"Cross-encoder 모델 로드 중: {self.model_name}")
            self._model = CrossEncoder(
                model_name_or_path=self.model_name,
                device=os.getenv("DEVICE", "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"),
                trust_remote_code=True
            )
            logger.info("Cross-encoder 모델 로드 완료.")

    def get_cross_encoder_scores(self, query: str, documents: list[str]) -> list[float]:
        if not documents:
            return []

        sentence_pairs = [[query, doc] for doc in documents]
        scores = self._model.predict(sentence_pairs).tolist()
        return scores

if __name__ == "__main__":
    setup_logger()
    logger.info("CrossEncoderModel 간단 테스트 실행 중...")

    model_instance = CrossEncoderModel()

    test_query = "부동산 매매 계약 해지"
    test_documents = [
        "부동산 매매 계약은 당사자 일방이 재산권을 상대방에게 이전할 것을 약정하고 상대방이 그 대금을 지급할 것을 약정함으로써 효력이 생긴다.",
        "계약 해지는 당사자 일방의 의사표시로 가능하며, 해지 시에는 원상회복의 의무가 발생한다.",
        "임대차 계약은 임대인이 임차인에게 목적물을 사용, 수익하게 하고 임차인이 이에 대한 차임을 지급할 것을 약정함으로써 성립한다."
    ]

    logger.info(f"\n질의: \"{test_query}\"")
    logger.info("문서 목록:")
    for i, doc in enumerate(test_documents):
        logger.info(f"  문서 {i+1}: \"{doc}\"")

    scores = model_instance.get_cross_encoder_scores(test_query, test_documents)

    logger.info("\n유사도 점수:")
    for i, score in enumerate(scores):
        logger.info(f"  문서 {i+1}: {score:.4f}")

    logger.info("테스트 완료.")
