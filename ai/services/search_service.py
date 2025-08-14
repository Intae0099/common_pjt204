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
        주어진 질의(query)에 대해 임베딩 유사도 기준으로 유사한 법률 문서 청크를 조회한다.
        재정렬 옵션(use_rerank)을 통해 Cross-encoder로 결과를 재정렬할 수 있다.
        """
        query_embedding = self.embedding_model.get_embedding(query)

        conn = None
        try:
            conn = get_psycopg2_connection()
            register_vector(conn)

            with conn.cursor() as cur:
                # 전체 개수
                cur.execute("SELECT COUNT(DISTINCT lc.case_id) FROM legal_chunks lch JOIN legal_cases lc ON lch.case_id = lc.case_id")
                total_count = cur.fetchone()[0]

                # 페이지네이션 검색
                offset = (page - 1) * size
                cur.execute(
                    """
                    SELECT lc.case_id, lc.title, lc.decision_date, lc.category, lc.issue, lc.summary, lc.full_text, lch.chunk_text, lc.statutes
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
                        "chunk_text": chunk_text,
                        "statutes": statutes
                    }
                    for cid, title, decision_date, category, issue, summary, full_text, chunk_text, statutes in cur.fetchall()
                ]

            # 🔧 DEBUG: 초기 검색 결과 → 제목 + 개수만 표시
            init_titles = [
                (doc.get("title") if isinstance(doc.get("title"), str) else str(doc.get("title")))
                for doc in initial_results
            ]
            logger.info(f"[search] count={len(initial_results)}, titles={init_titles}")

            if use_rerank:
                logger.info("Applying reranking to search results...")
                reranked = self._rerank_cases(query, initial_results)

                # 🔧 DEBUG: 재정렬 결과 → 제목 + 개수만 표시
                rerank_titles = [
                    (doc.get("title") if isinstance(doc.get("title"), str) else str(doc.get("title")))
                    for doc in reranked
                ]
                logger.info(f"[rerank] count={len(reranked)}, titles={rerank_titles}")

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
        Cross-encoder 모델을 사용하여 초기 검색 결과(청크 텍스트 우선)를 재평가하여 관련도 순으로 재정렬한다.
        """
        if not initial_results:
            return []

        documents_to_rerank = []
        for i, doc in enumerate(initial_results):
            # summary가 None인 경우가 많으므로 chunk_text를 우선 사용하고, 없으면 issue를 사용
            text_for_rerank = doc.get('chunk_text') or doc.get('issue') or doc.get('summary') or ""
            if not isinstance(text_for_rerank, str):
                text_for_rerank = str(text_for_rerank) if text_for_rerank is not None else ""
            documents_to_rerank.append(text_for_rerank)

        scores = self.cross_encoder_model.get_cross_encoder_scores(query, documents_to_rerank)

        scored_results = []
        for i, doc in enumerate(initial_results):
            doc['score'] = scores[i]
            scored_results.append(doc)

        reranked_results = sorted(scored_results, key=lambda x: x['score'], reverse=True)
        
        # 상위 3개만 반환
        top_3_results = reranked_results[:3]
        logger.info(f"Reranked {len(reranked_results)} cases, returning top {len(top_3_results)} based on Cross-encoder scores.")
        return top_3_results
