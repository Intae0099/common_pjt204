from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from llm.models.model_loader import ModelLoader
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel

# Create a simple FastAPI app for testing
app = FastAPI()

# Define dependency functions that use ModelLoader
def get_test_embedding_model() -> EmbeddingModel:
    return ModelLoader.get_embedding_model()

def get_test_cross_encoder_model() -> CrossEncoderModel:
    return ModelLoader.get_cross_encoder_model()

@app.get("/test-models")
async def test_models_endpoint(
    embedding_model: EmbeddingModel = Depends(get_test_embedding_model),
    cross_encoder_model: CrossEncoderModel = Depends(get_test_cross_encoder_model)
):
    return {
        "embedding_model_id": id(embedding_model),
        "cross_encoder_model_id": id(cross_encoder_model)
    }

client = TestClient(app)

def test_model_loader_singleton():
    # Test EmbeddingModel singleton
    model1_emb = ModelLoader.get_embedding_model()
    model2_emb = ModelLoader.get_embedding_model()
    assert model1_emb is model2_emb, "EmbeddingModel should be a singleton"

    # Test CrossEncoderModel singleton
    model1_ce = ModelLoader.get_cross_encoder_model()
    model2_ce = ModelLoader.get_cross_encoder_model()
    assert model1_ce is model2_ce, "CrossEncoderModel should be a singleton"

def test_fastapi_dependency_injection_uses_singleton():
    response1 = client.get("/test-models")
    response2 = client.get("/test-models")

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    # Verify that the same instance IDs are returned
    assert data1["embedding_model_id"] == data2["embedding_model_id"], \
        "FastAPI should inject the same EmbeddingModel instance"
    assert data1["cross_encoder_model_id"] == data2["cross_encoder_model_id"], \
        "FastAPI should inject the same CrossEncoderModel instance"

    # Optionally, verify that the IDs match the actual singleton instances
    assert data1["embedding_model_id"] == id(ModelLoader.get_embedding_model()), \
        "Injected EmbeddingModel ID should match singleton ID"
    assert data1["cross_encoder_model_id"] == id(ModelLoader.get_cross_encoder_model()), \
        "Injected CrossEncoderModel ID should match singleton ID"
