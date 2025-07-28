import pytest
from llm.models.embedding_model import load_model, get_embedding

def test_load_model():
    model = load_model()
    assert model is not None, "Model should be loaded"
    assert hasattr(model, 'encode'), "Loaded object should have an encode method"

def test_get_embedding():
    sample_text = "This is a test sentence."
    embedding = get_embedding(sample_text)
    assert isinstance(embedding, list), "Embedding should be a list"
    assert len(embedding) > 0, "Embedding list should not be empty"
    assert all(isinstance(x, float) for x in embedding), "All elements in embedding should be floats"
