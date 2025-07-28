import pytest
from unittest.mock import patch, MagicMock
import os

from llm.models.cross_encoder_model import load_cross_encoder_model, get_cross_encoder_scores, CROSS_ENCODER_MODEL_NAME
from services.search_service import rerank_cases

# Mock the CrossEncoder to prevent actual model loading during tests
@pytest.fixture(autouse=True)
def mock_cross_encoder():
    with patch('llm.models.cross_encoder_model.CrossEncoder') as MockCrossEncoder:
        mock_instance = MockCrossEncoder.return_value
        mock_instance.predict.return_value = MagicMock(tolist=lambda: [0.1, 0.9, 0.5]) # Default mock scores
        yield MockCrossEncoder # Yield the mock object itself
    load_cross_encoder_model.cache_clear() # Clear cache after test

@pytest.fixture
def mock_scores():
    return [0.1, 0.9, 0.5]

# ────────────────── llm/cross_encoder_model.py 테스트 ──────────────────

def test_load_cross_encoder_model(mock_cross_encoder):
    """Cross-encoder 모델이 올바르게 로드되는지 테스트"""
    model = load_cross_encoder_model()
    assert model is not None
    # Verify that the CrossEncoder was called with the correct model name
    mock_cross_encoder.assert_called_once_with(
        model_name_or_path=CROSS_ENCODER_MODEL_NAME,
        device=os.getenv("DEVICE", "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"),
        trust_remote_code=True
    )

def test_get_cross_encoder_scores(mock_scores):
    """get_cross_encoder_scores 함수가 올바른 스코어를 반환하는지 테스트"""
    query = "test query"
    documents = ["doc1", "doc2", "doc3"]
    scores = get_cross_encoder_scores(query, documents)

    assert isinstance(scores, list)
    assert len(scores) == len(documents)
    assert scores == mock_scores # Use the fixture for expected scores

def test_get_cross_encoder_scores_empty_documents():
    """빈 문서 리스트에 대해 get_cross_encoder_scores가 빈 리스트를 반환하는지 테스트"""
    query = "test query"
    documents = []
    scores = get_cross_encoder_scores(query, documents)
    assert scores == []

# ────────────────── modules/search_module.py의 rerank_cases() 테스트 ──────────────────

def test_rerank_cases_accuracy():
    """rerank_cases 함수가 스코어에 따라 정확하게 재정렬하는지 테스트"""
    query = "재정렬 테스트 질의"
    initial_results = [
        {"case_id": "C001", "summary": "첫 번째 문서 요약", "full_text": "..."},
        {"case_id": "C002", "summary": "두 번째 문서 요약", "full_text": "..."},
        {"case_id": "C003", "summary": "세 번째 문서 요약", "full_text": "..."},
    ]

    # get_cross_encoder_scores가 특정 스코어를 반환하도록 모의
    with patch('services.search_service.get_cross_encoder_scores', return_value=[0.1, 0.9, 0.5]) as mock_get_scores:
        reranked_docs = rerank_cases(query, initial_results)

        mock_get_scores.assert_called_once() # get_cross_encoder_scores가 호출되었는지 확인

        assert len(reranked_docs) == len(initial_results)

        # 스코어 기준으로 올바르게 정렬되었는지 확인 (내림차순)
        assert reranked_docs[0]['case_id'] == "C002" # Score 0.9
        assert reranked_docs[1]['case_id'] == "C003" # Score 0.5
        assert reranked_docs[2]['case_id'] == "C001" # Score 0.1

        # 각 문서에 score 필드가 추가되었는지 확인
        for doc in reranked_docs:
            assert 'score' in doc
            assert isinstance(doc['score'], float)

def test_rerank_cases_empty_results():
    """빈 초기 결과 리스트에 대해 rerank_cases가 빈 리스트를 반환하는지 테스트"""
    query = "test query"
    initial_results = []
    reranked_docs = rerank_cases(query, initial_results)
    assert reranked_docs == []

def test_rerank_cases_with_none_summary():
    """summary가 None인 경우에도 rerank_cases가 작동하는지 테스트"""
    query = "test query"
    initial_results = [
        {"case_id": "C001", "summary": "Valid summary", "full_text": "..."},
        {"case_id": "C002", "summary": None, "full_text": "..."}, # None summary
        {"case_id": "C003", "summary": "Another valid summary", "full_text": "..."},
    ]

    # get_cross_encoder_scores가 특정 스코어를 반환하도록 모의
    # None이 빈 문자열로 변환되므로, 해당 위치의 스코어도 예상해야 함
    with patch('services.search_service.get_cross_encoder_scores', return_value=[0.8, 0.2, 0.6]) as mock_get_scores:
        reranked_docs = rerank_cases(query, initial_results)

        mock_get_scores.assert_called_once()

        assert len(reranked_docs) == len(initial_results)

        # 스코어 기준으로 올바르게 정렬되었는지 확인
        assert reranked_docs[0]['case_id'] == "C001" # Score 0.8
        assert reranked_docs[1]['case_id'] == "C003" # Score 0.6
        assert reranked_docs[2]['case_id'] == "C002" # Score 0.2 (None -> "")

        for doc in reranked_docs:
            assert 'score' in doc
            assert isinstance(doc['score'], float)
