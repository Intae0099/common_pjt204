import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
import textwrap

from config.db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from db.database import get_psycopg2_connection
from utils.logger import setup_logger, get_logger

# ────────────────── 로거 설정 ──────────────────
setup_logger()
logger = get_logger(__name__)

# ────────────────── 전역 모델 캐싱 ──────────────────
_model = None

def _get_model():
    """
    SentenceTransformer 모델을 전역으로 1회만 로드하여 재사용한다.
    """
    global _model
    if _model is None:
        logger.info("SentenceTransformer 모델 로드 중...")
        _model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
        logger.info("SentenceTransformer 모델 로드 완료.")
    return _model


def search_similar_documents(query: str, limit: int = 10) -> list[dict]:
    """
    주어진 질의(query)에 대해 임베딩 유사도 기준으로
    유사한 법률 문서 청크를 조회한다.

    매개변수
    ----------
    query : str
        검색어(자연어 문장 또는 키워드).
    limit : int, 기본값 10
        반환할 결과 개수(Top‑K).

    반환값
    ----------
    list[dict]
        각 요소가 {'case_id': str, 'chunk_text': str} 형태인 리스트.
        DB 오류나 예외 발생 시 빈 리스트를 반환한다.
    """
    # 1) 질의 임베딩 생성
    model = _get_model()
    query_embedding = model.encode(query).tolist()

    conn = None
    try:
        # 2) 데이터베이스 연결
        conn = get_psycopg2_connection()
        register_vector(conn)

        # 3) 벡터 유사도(embedding <-> query) 오름차순 정렬 후 Top‑K 조회
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT case_id, chunk_text
                FROM   legal_chunks
                ORDER  BY embedding <-> %s::vector
                LIMIT  %s
                """,
                (query_embedding, limit)
            )
            return [
                {"case_id": cid, "chunk_text": txt}
                for cid, txt in cur.fetchall()
            ]

    except psycopg2.Error as e:
        logger.error(f"데이터베이스 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        return []
    finally:
        if conn:
            conn.close()



# ────────────────── 모듈 직접 실행 시 테스트 ──────────────────
if __name__ == '__main__':
    sample_query = "회사 자료를 가져오고 퇴사를 했습니다"
    print(f"\n[검색 질의] {sample_query}\n")

    docs = search_similar_documents(sample_query, limit=5)

    if not docs:
        print("⚠️  검색 결과가 없습니다.")
    else:
        for i, doc in enumerate(docs, 1):
            # 청크 텍스트 1줄 요약 (최대 120자)
            snippet = textwrap.shorten(doc['chunk_text'].replace("\n", " "),
                                       width=120,
                                       placeholder=" …")
            print(f"{i:02d}. Case ID: {doc['case_id']}")
            print(f"    {snippet}")
            print("-" * 80)