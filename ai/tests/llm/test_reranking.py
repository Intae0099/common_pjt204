import pytest
from unittest.mock import AsyncMock
from llm.models.cross_encoder_model import CrossEncoderModel
from llm.models.embedding_model import EmbeddingModel
from services.search_service import SearchService

@pytest.fixture(autouse=True)
def mock_search_service_for_reranking():
    embedding_model = AsyncMock(spec=EmbeddingModel)
    cross_encoder_model = AsyncMock(spec=CrossEncoderModel)
    service = SearchService(embedding_model, cross_encoder_model)
    yield service

def test_rerank_cases_sorting(mock_search_service_for_reranking, monkeypatch):
    """rerank_cases가 stub된 점수대로 내림차순 정렬하는지 확인"""
    search_service = mock_search_service_for_reranking
    query = "테스트 질의"
    docs = [
        {"case_id": "A", "summary": "요약A", "full_text": ""},
        {"case_id": "B", "summary": "요약B", "full_text": ""},
        {"case_id": "C", "summary": "요약C", "full_text": ""},
    ]

    fake_scores = [0.3, 0.9, 0.1]
    monkeypatch.setattr(search_service.cross_encoder_model, "get_cross_encoder_scores", lambda q, d: fake_scores)

    reranked = search_service._rerank_cases(query, docs)
    assert [d["case_id"] for d in reranked] == ["B", "A", "C"]
    assert all(isinstance(d.get("score"), float) for d in reranked)
