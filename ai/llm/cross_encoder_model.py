from sentence_transformers import CrossEncoder
from functools import lru_cache
import os
from utils.logger import setup_logger, get_logger  # setup_logger와 get_logger 임포트

# 모듈 로거 초기화
logger = get_logger(__name__)

# 사용할 Cross‑encoder 모델 이름
CROSS_ENCODER_MODEL_NAME = "Alibaba-NLP/gte-multilingual-base"

@lru_cache(maxsize=1)  # 로드한 모델 캐싱
def load_cross_encoder_model():
    """
    Cross‑encoder 모델(Alibaba‑NLP/gte‑multilingual‑base)을 캐싱하여 로드합니다.
    """
    logger.info(f"Cross‑encoder 모델 로드 중: {CROSS_ENCODER_MODEL_NAME}")
    model = CrossEncoder(
        model_name_or_path=CROSS_ENCODER_MODEL_NAME,
        device=os.getenv("DEVICE", "gpu" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"),  # GPU가 설정되어 있으면 GPU 사용
        trust_remote_code=True    # 커스텀 코드 허용
    )
    logger.info("Cross‑encoder 모델 로드 완료.")
    return model

def get_cross_encoder_scores(query: str, documents: list[str]) -> list[float]:
    """
    주어진 질의(query)와 문서 목록(documents)에 대해 Cross‑encoder를 사용해 유사도 점수를 계산합니다.

    Args:
        query (str): 사용자 질의
        documents (list[str]): 점수를 계산할 문서 텍스트 목록

    Returns:
        list[float]: 문서별 유사도 점수 리스트
    """
    model = load_cross_encoder_model()
    if not documents:
        return []

    # 예측을 위해 [질의, 문서] 쌍 생성
    sentence_pairs = [[query, doc] for doc in documents]

    # 점수 계산 및 리스트 변환
    scores = model.predict(sentence_pairs).tolist()
    return scores

if __name__ == "__main__":
    # 메인 실행 시 로거 설정
    setup_logger()
    logger.info("cross_encoder_model.py 간단 테스트 실행 중...")

    # 테스트용 예시 질의 및 문서
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

    scores = get_cross_encoder_scores(test_query, test_documents)

    logger.info("\n유사도 점수:")
    for i, score in enumerate(scores):
        logger.info(f"  문서 {i+1}: {score:.4f}")

    # 빈 문서 리스트 테스트
    logger.info("\n빈 문서 리스트로 테스트 중...")
    empty_scores = get_cross_encoder_scores(test_query, [])
    logger.info(f"빈 리스트 점수: {empty_scores}")

    logger.info("테스트 완료.")
