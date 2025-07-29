import psycopg2
from pgvector.psycopg2 import register_vector
import os
from dotenv import load_dotenv

from db.database import get_psycopg2_connection
from utils.logger import setup_logger, get_logger
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel

load_dotenv()

# ────────────────── 로거 설정 ──────────────────
setup_logger()
logger = get_logger(__name__)

def search_cases(
    query: str,
    embedding_model: EmbeddingModel,
    cross_encoder_model: CrossEncoderModel,
    top_k: int = 5,
    use_rerank: bool = True
) -> list[dict]:
    """
    주어진 질의(query)에 대해 임베딩 유사도 기준으로
    유사한 법률 문서 청크를 조회한다.
    재정렬 옵션(use_rerank)을 통해 Cross-encoder로 결과를 재정렬할 수 있다.

    매개변수
    ----------
    query : str
        검색어(자연어 문장 또는 키워드).
    embedding_model : EmbeddingModel
        임베딩 모델 인스턴스.
    cross_encoder_model : CrossEncoderModel
        크로스 인코더 모델 인스턴스.
    top_k : int, 기본값 5
        반환할 결과 개수(Top-K).
    use_rerank : bool, 기본값 True
        Cross-encoder를 사용하여 검색 결과를 재정렬할지 여부.

    반환값
    ----------
    list[dict]
        각 요소가 {'case_id': str, 'summary': str, 'full_text': str, 'score': float(재정렬 시)} 형태인 리스트.
        DB 오류나 예외 발생 시 빈 리스트를 반환한다.
    """
    # 1) 질의 임베딩 생성
    query_embedding = embedding_model.get_embedding(query)

    conn = None
    try:
        # 2) 데이터베이스 연결
        conn = get_psycopg2_connection()
        register_vector(conn)

        # 3) 벡터 유사도(embedding <-> query) 오름차순 정렬 후 Top-K 조회
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT lc.case_id,lc.title,lc.decision_date,lc.category, lc.full_text, lch.chunk_text
                FROM legal_chunks lch
                JOIN legal_cases lc ON lch.case_id = lc.case_id
                ORDER BY lch.embedding <-> %s::vector
                LIMIT %s
                """,
                (query_embedding, top_k)
            )
            initial_results = [
                {"case_id": cid, "title": title, "decision_date": decision_date, "category": category, "full_text": full_text, "chunk_text": chunk_text}
                for cid, title, decision_date, category, full_text, chunk_text in cur.fetchall()
            ]

        # 벡터 검색 결과 개수 로그
        logger.info(f"Vector search 결과 개수: {len(initial_results)}")

        if use_rerank:
            logger.info("Applying reranking to search results...")
            reranked = rerank_cases(query, initial_results, cross_encoder_model)
            # 재정렬 후 상위 3개만 추출
            reranked_top3 = reranked[:3]
            logger.info(f"Reranked 결과 개수(상위 3개): {len(reranked_top3)}")
            return reranked_top3
        else:
            logger.info("Reranking skipped.")
            return initial_results

    except psycopg2.Error as e:
        logger.error(f"데이터베이스 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        return []
    finally:
        if conn:
            conn.close()

def rerank_cases(query: str, initial_results: list[dict], cross_encoder_model: CrossEncoderModel) -> list[dict]:
    """
    Cross-encoder 모델을 사용하여 초기 검색 결과(판례 요약)를 재평가하여 관련도 순으로 재정렬한다.

    매개변수
    ----------
    query : str
        사용자 질의.
    initial_results : list[dict]
        초기 검색 결과. 각 요소는 {'case_id': str, 'summary': str, 'full_text': str} 형태.
    cross_encoder_model : CrossEncoderModel
        크로스 인코더 모델 인스턴스.

    반환값
    ----------
    list[dict]
        재정렬된 검색 결과. 각 요소는 초기 결과와 동일한 형태이며, score 필드가 추가된다.
    """
    if not initial_results:
        return []

    documents_to_rerank = []
    for i, doc in enumerate(initial_results):
        summary = doc.get('summary')
        if not isinstance(summary, str):
            logger.warning(f"Document {i} (Case ID: {doc.get('case_id', 'N/A')}) has non-string summary: Type={type(summary)}, Value={summary}")
            # Convert to string to prevent error, or handle as appropriate (e.g., skip)
            summary = str(summary) if summary is not None else ""
        documents_to_rerank.append(summary)
    scores = cross_encoder_model.get_cross_encoder_scores(query, documents_to_rerank)

    # 결과에 스코어 추가
    scored_results = []
    for i, doc in enumerate(initial_results):
        doc['score'] = scores[i]
        scored_results.append(doc)

    # 스코어 기준으로 내림차순 정렬
    reranked_results = sorted(scored_results, key=lambda x: x['score'], reverse=True)

    logger.info(f"Reranked {len(reranked_results)} cases based on Cross-encoder scores.")
    return reranked_results


# ────────────────── 모듈 직접 실행 시 테스트 ──────────────────
if __name__ == '__main__':
    setup_logger()
    logger.info("\n[검색 질의 테스트 시작]\n")

    sample_query = "회사 자료를 가져오고 퇴사를 했습니다"
    logger.info(f"검색어: {sample_query}\n")

    # 1) 재정렬 적용된 결과
    logger.info("▶ 재정렬 적용 결과")
    # Note: For direct execution, you might need to instantiate models here or adjust for testing.
    # This part will need to be updated to reflect the new model loading.
    # For now, leaving it as is, but it won't work without model instances.
    # results_reranked = search_cases(sample_query, top_k=5, use_rerank=True)
    logger.info("Direct execution of search_cases is not supported without model instances. Please run via FastAPI app.")

    logger.info("\n[검색 질의 테스트 완료]")