import pytest
from llm.models.model_loader import ModelLoader
from llm.models.cross_encoder_model import CrossEncoderModel
from services.search_service import rerank_cases

@pytest.fixture(autouse=True)
def clear_model_loader():
    # 싱글턴 캐시 초기화
    ModelLoader._cross_encoder_model = None
    yield
    ModelLoader._cross_encoder_model = None

def test_model_loader_singleton():
    """ModelLoader가 같은 인스턴스를 반환하는지 확인"""
    m1 = ModelLoader.get_cross_encoder_model()
    m2 = ModelLoader.get_cross_encoder_model()
    assert isinstance(m1, CrossEncoderModel)
    assert m1 is m2

def test_rerank_cases_sorting(monkeypatch):
    """rerank_cases가 stub된 점수대로 내림차순 정렬하는지 확인"""
    query = "테스트 질의"
    docs = [
        {"case_id": "A", "summary": "요약A", "full_text": ""},
        {"case_id": "B", "summary": "요약B", "full_text": ""},
        {"case_id": "C", "summary": "요약C", "full_text": ""},
    ]

    fake_scores = [0.3, 0.9, 0.1]
    model = ModelLoader.get_cross_encoder_model()
    monkeypatch.setattr(model, "get_cross_encoder_scores", lambda q, d: fake_scores)

    reranked = rerank_cases(query, docs, model)
    # Score 내림차순 정렬 순서: B(0.9), A(0.3), C(0.1)
    assert [d["case_id"] for d in reranked] == ["B", "A", "C"]
    # 각 문서에 score 필드가 float 타입으로 추가되었는지 확인
    assert all(isinstance(d.get("score"), float) for d in reranked)
