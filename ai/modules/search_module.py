import psycopg2
from pgvector.psycopg2 import register_vector
import os
from dotenv import load_dotenv

from db.database import get_psycopg2_connection
from utils.logger import setup_logger, get_logger
from llm.embedding_model import get_embedding
from llm.cross_encoder_model import get_cross_encoder_scores

load_dotenv()

# ────────────────── 로거 설정 ──────────────────
setup_logger()
logger = get_logger(__name__)

def search_cases(query: str, top_k: int = 5, use_rerank: bool = True) -> list[dict]:
    """
    주어진 질의(query)에 대해 임베딩 유사도 기준으로
    유사한 법률 문서 청크를 조회한다.
    재정렬 옵션(use_rerank)을 통해 Cross-encoder로 결과를 재정렬할 수 있다.

    매개변수
    ----------
    query : str
        검색어(자연어 문장 또는 키워드).
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
    query_embedding = get_embedding(query)

    conn = None
    try:
        # 2) 데이터베이스 연결
        conn = get_psycopg2_connection()
        register_vector(conn)

        # 3) 벡터 유사도(embedding <-> query) 오름차순 정렬 후 Top-K 조회
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
            initial_results = [
                {"case_id": cid, "summary": summary, "full_text": full_text}
                for cid, summary, full_text in cur.fetchall()
            ]

        if use_rerank:
            logger.info("Applying reranking to search results...")
            return rerank_cases(query, initial_results)
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

def rerank_cases(query: str, initial_results: list[dict]) -> list[dict]:
    """
    Cross-encoder 모델을 사용하여 초기 검색 결과(판례 요약)를 재평가하여 관련도 순으로 재정렬한다.

    매개변수
    ----------
    query : str
        사용자 질의.
    initial_results : list[dict]
        초기 검색 결과. 각 요소는 {'case_id': str, 'summary': str, 'full_text': str} 형태.

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
    scores = get_cross_encoder_scores(query, documents_to_rerank)

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
    results_reranked = search_cases(sample_query, top_k=5, use_rerank=True)
    if not results_reranked:
        logger.warning("검색 결과가 없습니다.")
    else:
        for idx, doc in enumerate(results_reranked, start=1):
            logger.info(f"{idx}. Case ID: {doc['case_id']}")
            logger.info(f"   Summary : {doc['summary'] or '[요약 없음]'}")
            # preview = doc['full_text'][:100].replace("\n", " ")
            # logger.info(f"   Preview : {preview}...")
            # logger.info(f"   Score   : {doc.get('score', 0):.4f}")
            # logger.info("-" * 80)

    # 2) 재정렬 미적용 결과
    logger.info("\n▶ 재정렬 미적용 결과")
    results_original = search_cases(sample_query, top_k=5, use_rerank=False)
    if not results_original:
        logger.warning("검색 결과가 없습니다.")
    else:
        for idx, doc in enumerate(results_original, start=1):
            logger.info(f"{idx}. Case ID: {doc['case_id']}")
            logger.info(f"   Summary : {doc['summary'] or '[요약 없음]'}")
            # preview = doc['full_text'][:100].replace("\n", " ")
            # logger.info(f"   Preview : {preview}...")
            # logger.info("-" * 80)

    logger.info("\n[검색 질의 테스트 완료]")