import psycopg2
from pgvector.psycopg2 import register_vector
import os
from dotenv import load_dotenv
from datetime import date

from db.database import get_psycopg2_connection
from utils.logger import setup_logger, get_logger
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel

load_dotenv()

# ────────────────── 로거 설정 ──────────────────
setup_logger()
logger = get_logger(__name__)

class SearchService:
    def __init__(self, embedding_model: EmbeddingModel, cross_encoder_model: CrossEncoderModel):
        self.embedding_model = embedding_model
        self.cross_encoder_model = cross_encoder_model

    async def vector_search(self, query: str, page: int = 1, size: int = 10, use_rerank: bool = True) -> tuple[list[dict], int]:
        """
        주어진 질의(query)에 대해 임베딩 유사도 기준으로
        유사한 법률 문서 청크를 조회한다.
        재정렬 옵션(use_rerank)을 통해 Cross-encoder로 결과를 재정렬할 수 있다.

        매개변수
        ----------
        query : str
            검색어(자연어 문장 또는 키워드).
        page : int, 기본값 1
            페이지 번호.
        size : int, 기본값 10
            페이지 당 결과 개수.
        use_rerank : bool, 기본값 True
            Cross-encoder를 사용하여 검색 결과를 재정렬할지 여부.

        반환값
        ----------
        tuple[list[dict], int]
            각 요소가 {'case_id': str, 'title': str, 'decision_date': date, 'category': str, 'summary': str, 'full_text': str} 형태인 리스트와 총 결과 개수.
            DB 오류나 예외 발생 시 빈 리스트와 0을 반환한다.
        """
        query_embedding = self.embedding_model.get_embedding(query)

        conn = None
        try:
            conn = get_psycopg2_connection()
            register_vector(conn)

            with conn.cursor() as cur:
                # 먼저 전체 개수를 가져옵니다.
                cur.execute("SELECT COUNT(DISTINCT lc.case_id) FROM legal_chunks lch JOIN legal_cases lc ON lch.case_id = lc.case_id")
                total_count = cur.fetchone()[0]

                # 페이지네이션을 고려하여 검색합니다.
                offset = (page - 1) * size
                cur.execute(
                    """
                    SELECT lc.case_id, lc.title, lc.decision_date, lc.category, lc.issue, lc.summary, lc.full_text, lch.chunk_text
                    FROM legal_chunks lch
                    JOIN legal_cases lc ON lch.case_id = lc.case_id
                    ORDER BY lch.embedding <-> %s::vector
                    LIMIT %s OFFSET %s
                    """,
                    (query_embedding, size, offset)
                )
                initial_results = [
                    {
                        "case_id": cid,
                        "title": title,
                        "decision_date": decision_date,
                        "category": category,
                        "issue": issue,
                        "summary": summary,
                        "full_text": full_text,
                        "chunk_text": chunk_text
                    }
                    for cid, title, decision_date, category, issue, summary, full_text, chunk_text in cur.fetchall()
                ]
            logger.debug(f"Initial search results: {initial_results}")

            if use_rerank:
                logger.info("Applying reranking to search results...")
                reranked = self._rerank_cases(query, initial_results)
                logger.debug(f"Reranked results: {reranked}")
                return reranked, total_count
            else:
                logger.info("Reranking skipped.")
                return initial_results, total_count

        except psycopg2.Error as e:
            logger.error(f"데이터베이스 오류: {e}")
            return [], 0
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return [], 0
        finally:
            if conn:
                conn.close()

    async def get_case_by_id(self, prec_id: str) -> dict | None:
        """
        판례 ID로 판례의 상세 정보를 조회합니다.

        매개변수
        ----------
        prec_id : str
            판례 ID.

        반환값
        ----------
        dict | None
            판례 상세 정보 딕셔너리 또는 찾을 수 없는 경우 None.
        """
        conn = None
        try:
            conn = get_psycopg2_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT case_id, title, decision_date, category, issue, summary, statutes, precedents, full_text
                    FROM legal_cases
                    WHERE case_id = %s
                    """,
                    (prec_id,)
                )
                result = cur.fetchone()
                if result:
                    columns = [desc[0] for desc in cur.description]
                    return dict(zip(columns, result))
                return None
        except psycopg2.Error as e:
            logger.error(f"데이터베이스 오류: {e}")
            return None
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def _rerank_cases(self, query: str, initial_results: list[dict]) -> list[dict]:
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
                summary = str(summary) if summary is not None else ""
            documents_to_rerank.append(summary)
        scores = self.cross_encoder_model.get_cross_encoder_scores(query, documents_to_rerank)

        scored_results = []
        for i, doc in enumerate(initial_results):
            doc['score'] = scores[i]
            scored_results.append(doc)

        reranked_results = sorted(scored_results, key=lambda x: x['score'], reverse=True)

        logger.info(f"Reranked {len(reranked_results)} cases based on Cross-encoder scores.")
        return reranked_results
