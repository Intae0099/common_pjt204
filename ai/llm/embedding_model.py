from sentence_transformers import SentenceTransformer
from typing import List

_model = None
_model_name: str = ""

def load_model(model_name: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS") -> SentenceTransformer:
    global _model, _model_name
    if _model is None:
        _model = SentenceTransformer(model_name)
        _model_name = model_name
    return _model

def get_embedding(text: str) -> List[float]:
    model = load_model()
    embedding = model.encode(text)
    return embedding.tolist()

if __name__ == '__main__':
    # Example usage
    model = load_model()  
    # model_name_or_path 대신 저장해 둔 변수 출력
    print(f"Model loaded: {_model_name}")

    text = "This is an example sentence."
    embedding = get_embedding(text)
    print(f"Embedding for '{text}': {embedding[:5]}...")  # Print first 5 elements
    print(f"Embedding dimension: {len(embedding)}")
