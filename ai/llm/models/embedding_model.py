from typing import List

import torch
from utils.logger import setup_logger, get_logger

# ────────────────── 로거 설정 ──────────────────
setup_logger()
logger = get_logger(__name__)

# 전역 모델 캐시 변수
_model = None
_model_name: str = ""

def load_model(model_name: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"):
    """
    SentenceTransformer 모델을 로드하고 캐싱합니다.
    (함수 내부에서만 import, 모듈 로드 시점의 메모리 사용 최소화)
    """
    global _model, _model_name
    if _model is None:
        logger.info(f"SentenceTransformer 모델 로드 중: {model_name}")
        # 필요한 시점에만 모델을 불러옵니다.
        from sentence_transformers import SentenceTransformer
        logger.info(f"SentenceTransformer 모델 로드 중: {model_name} (device=cpu)")
        _model = SentenceTransformer(model_name, device="cpu")
        _model_name = model_name
        logger.info("SentenceTransformer 모델 로드 완료.")
    return _model

def get_embedding(text: str) -> List[float]:
    """
    주어진 텍스트를 임베딩 벡터로 변환합니다.
    """
    model = load_model()
    logger.debug(f"텍스트 인코딩 시도: 타입={type(text)}, 값 일부={text[:100]}...")
    # 배치 사이즈 줄여 메모리 절약
    embedding = model.encode(text, batch_size=1, convert_to_numpy=True)
    return embedding.tolist()

if __name__ == '__main__':
    # 예시 실행
    model = load_model()
    logger.info(f"로드된 모델: {_model_name}")

    sample_text = "이것은 예시 문장입니다."
    embedding = get_embedding(sample_text)

    logger.info(f"텍스트 '{sample_text}' 임베딩 일부: {embedding[:5]}...")
    logger.info(f"임베딩 차원: {len(embedding)}")
