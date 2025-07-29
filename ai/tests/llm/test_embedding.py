import pytest
from llm.models.embedding_model import EmbeddingModel
from llm.models.model_loader import ModelLoader

@pytest.fixture(scope="module")
def embedding_model_instance():
    return ModelLoader.get_embedding_model()

def test_load_model(embedding_model_instance):
    assert isinstance(embedding_model_instance, EmbeddingModel), "Model should be an instance of EmbeddingModel"
    assert hasattr(embedding_model_instance._model, 'encode'), "Loaded model object should have an encode method"

def test_get_embedding(embedding_model_instance):
    sample_text = "This is a test sentence."
    embedding = embedding_model_instance.get_embedding(sample_text)
    assert isinstance(embedding, list), "Embedding should be a list"
    assert len(embedding) > 0, "Embedding list should not be empty"
    assert all(isinstance(x, float) for x in embedding), "All elements in embedding should be floats"
