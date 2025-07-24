import psycopg2
from pgvector.psycopg2 import register_vector
import os
from dotenv import load_dotenv

from db.database import get_psycopg2_connection
from utils.logger import setup_logger, get_logger
from llm.embedding_model import get_embedding

load_dotenv()

# ────────────────── 로거 설정 ──────────────────
setup_logger()
logger = get_logger(__name__)

def search_cases(query: str, top_k: int = 5) -> list[dict]:
    """
    주어진 질의(query)에 대해 임베딩 유사도 기준으로
    유사한 법률 문서 청크를 조회한다.

    매개변수
    ----------
    query : str
        검색어(자연어 문장 또는 키워드).
    top_k : int, 기본값 5
        반환할 결과 개수(Top‑K).

    반환값
    ----------
    list[dict]
        각 요소가 {'case_id': str, 'summary': str} 형태인 리스트.
        DB 오류나 예외 발생 시 빈 리스트를 반환한다.
    """
    # 1) 질의 임베딩 생성
    query_embedding = get_embedding(query)

    conn = None
    try:
        # 2) 데이터베이스 연결
        conn = get_psycopg2_connection()
        register_vector(conn)

        # 3) 벡터 유사도(embedding <-> query) 오름차순 정렬 후 Top‑K 조회
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT lc.case_id, lc.summary, lc.full_text
                FROM legal_chunks lch
                JOIN legal_cases lc ON lch.case_id = lc.case_id
                ORDER BY lch.embedding <-> %s::vector
                LIMIT %s
                """,
                (query_embedding, top_k)
            )
            return [
                {"case_id": cid, "summary": summary, "full_text": full_text}
                for cid, summary, full_text in cur.fetchall()
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

    docs = search_cases(sample_query, top_k=5)

    if not docs:
        print("⚠️  검색 결과가 없습니다.")
    else:
        for i, doc in enumerate(docs, 1):
            print(f"{i:02d}. Case ID: {doc['case_id']}")
            print(f"    Summary : {doc['summary']}")
            # full_text의 앞 100글자만 출력
            preview = doc['full_text'][:100].replace("\n", " ")
            print(f"    Preview : {preview}...")
            print("-" * 80)
