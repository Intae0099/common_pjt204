import psycopg2
from pgvector.psycopg2 import register_vector
import os
from dotenv import load_dotenv
from datetime import date

from db.database import get_psycopg2_connection
from utils.logger import setup_logger, get_logger
from utils.exceptions import DatabaseError, SearchError, handle_service_exceptions
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel
from services.bm25_service import BM25Service

load_dotenv()

# ────────────────── 로거 설정 ──────────────────
setup_logger()
logger = get_logger(__name__)

class SearchService:
    def __init__(self, embedding_model: EmbeddingModel, cross_encoder_model: CrossEncoderModel, bm25_service: BM25Service):
        self.embedding_model = embedding_model
        self.cross_encoder_model = cross_encoder_model
        self.bm25_service = bm25_service

    async def vector_search(self, query: str, page: int = 1, size: int = 10, use_rerank: bool = True) -> tuple[list[dict], int]:
        """
        BM25를 사용한 키워드 기반 검색 후, Cross-encoder로 재정렬(rerank)을 수행합니다.
        """
        try:
            logger.info(f"BM25 검색 시작: query='{query}', size={size}")
            # 1단계: BM25를 사용하여 후보군 검색 (재정렬을 위해 size보다 많은 30개 후보 확보)
            initial_results = self.bm25_service.search(query, top_n=30)
            
            # BM25 결과에 소스 정보 추가
            for r in initial_results:
                r['_source'] = 'bm25'
                r['chunk_text'] = '' # rerank 호환성을 위해 추가

            total_count = len(initial_results)
            logger.info(f"BM25 검색 결과 {total_count}개 후보 확보.")

            if use_rerank and len(initial_results) > 1:
                logger.info("Cross-encoder 재정렬 적용...")
                reranked_results = self._rerank_cases(query, initial_results, requested_size=size)
                
                final_bm25 = len([r for r in reranked_results if r.get("_source") == "bm25"])
                logger.info(f"[final_results] total={len(reranked_results)} (bm25={final_bm25})")

                return reranked_results, total_count
            else:
                logger.info("재정렬(reranking)이 비활성화되었거나 결과가 부족합니다.")
                return initial_results[:size], total_count

        except Exception as e:
            logger.error(f"판례 검색 중 예상치 못한 오류 발생: {e}", exc_info=True)
            raise SearchError(f"판례 검색 중 오류가 발생했습니다: {str(e)}", original_exception=e)


    async def high_precision_search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        AI 사전 상담용 고정밀도 검색
        BM25와 벡터 검색으로 후보군을 생성하고, 2단계 필터링과 Cross-encoder로 최종 결과를 도출합니다.
        """
        conn = None
        try:
            # 1단계: 하이브리드 방식으로 대량 후보 수집
            logger.info(f"[high_precision] 1단계: 하이브리드 후보 수집 시작 (query: {query})")
            
            # 1-1. BM25 검색 (40개)
            bm25_candidates = self.bm25_service.search(query, top_n=40)
            for r in bm25_candidates:
                r['_source'] = 'bm25'
                r['chunk_text'] = ''
                r['_score'] = 0

            # 1-2. 벡터 검색 (20개, BM25 결과 제외)
            bm25_case_ids = {c["case_id"] for c in bm25_candidates}
            vector_candidates = []
            
            query_embedding = self.embedding_model.get_embedding(query)

            # 임베딩 생성 결과가 유효한 벡터인지 확인
            if isinstance(query_embedding, list) and len(query_embedding) > 0:
                conn = None # conn 변수 초기화
                try:
                    conn = get_psycopg2_connection()
                    register_vector(conn)
                    with conn.cursor() as cur:
                        exclude_clause = ""
                        exclude_params = []
                        if bm25_case_ids:
                            placeholders = ",".join(["%s"] * len(bm25_case_ids))
                            exclude_clause = f"AND lc.case_id NOT IN ({placeholders})"
                            exclude_params = list(bm25_case_ids)
                        
                        vector_query = f"""                            
                        SELECT lc.case_id, lc.title, lc.decision_date, lc.category,                                    
                        lc.issue, lc.summary, lc.full_text, lch.chunk_text, lc.statutes,                                   
                        lch.embedding <-> %s::vector as distance                            
                        FROM legal_chunks lch                            
                        JOIN legal_cases lc ON lch.case_id = lc.case_id                           
                        WHERE 1=1 {exclude_clause}                            
                        ORDER BY lch.embedding <-> %s::vector                            
                        LIMIT 20                        
                        """
                        
                        cur.execute(vector_query, [query_embedding] + exclude_params + [query_embedding])
                        
                        for row in cur.fetchall():
                            vector_candidates.append({
                                "case_id": row[0],
                                "title": row[1],
                                "decision_date": row[2],
                                "category": row[3],
                                "issue": row[4],
                                "summary": row[5],
                                "full_text": row[6],
                                "chunk_text": row[7],
                                "statutes": row[8],
                                "_source": "vector",
                                "_score": 1.0 / (1.0 + row[9])  # distance -> similarity 변환
                            })
                finally:
                    if conn:
                        conn.close()
            else:
                logger.warning(f"쿼리 '{query}'에 대한 벡터 임베딩 생성에 실패하여 벡터 검색을 건너뜁니다.")

            # 1-3. 후보군 결합
            all_candidates = bm25_candidates + vector_candidates
            logger.info(f"[high_precision] 1단계 완료: {len(all_candidates)}개 후보 (bm25: {len(bm25_candidates)}, vector: {len(vector_candidates)})")
            
            if not all_candidates:
                logger.warning("[high_precision] 후보가 없어 빈 결과 반환")
                return []
            
            # 2단계: 관련성 점수 재계산 및 필터링 (기존 로직 유지)
            logger.info("[high_precision] 2단계: 정확도 필터링 시작")
            
            filtered_candidates = []
            query_lower = query.lower()
            
            for candidate in all_candidates:
                title = (candidate.get("title") or "").lower()
                category = (candidate.get("category") or "").lower()
                
                relevance_score = 0.0
                if query_lower in title:
                    relevance_score += 3.0
                if query_lower in category:
                    relevance_score += 2.0
                
                legal_term_map = {
                    "횡령": ["횡령", "배임", "특정경제범죄"], "사기": ["사기", "편취", "기망"],
                    "교통사고": ["교통사고", "교통", "자동차"], "손해배상": ["손해배상", "배상", "피해"],
                    "계약": ["계약", "약정", "합의"], "이혼": ["이혼", "혼인", "가사"],
                    "상속": ["상속", "유산", "유언"]
                }
                
                for main_term, related_terms in legal_term_map.items():
                    if main_term in query_lower:
                        for term in related_terms:
                            if term in title:
                                relevance_score += 2.0
                                break
                
                relevance_score += candidate.get("_score", 0.0) # 벡터 검색 점수 추가

                if relevance_score >= 1.0:
                    candidate["_relevance"] = relevance_score
                    filtered_candidates.append(candidate)
            
            filtered_candidates.sort(key=lambda x: x["_relevance"], reverse=True)
            filtered_candidates = filtered_candidates[:15]
            logger.info(f"[high_precision] 2단계 완료: {len(filtered_candidates)}개 필터링됨")
            
            if not filtered_candidates:
                logger.warning("[high_precision] 필터링 후 결과 없음")
                return []
            
            # 3단계: Cross-encoder 최종 선별
            logger.info(f"[high_precision] 3단계: 최종 {top_k}개 선별")
            
            if len(filtered_candidates) <= top_k:
                final_results = filtered_candidates
            else:
                final_results = self._rerank_cases(query, filtered_candidates, requested_size=top_k)
            
            logger.info(f"[high_precision] 완료: {len(final_results)}개 반환")
            
            if final_results:
                top_title = final_results[0].get("title", "N/A")
                top_source = final_results[0].get("_source", "N/A")
                top_relevance = final_results[0].get("_relevance", 0)
                logger.info(f"[high_precision] Top result: '{top_title}' (source: {top_source}, relevance: {top_relevance:.2f})")
            
            return final_results

        except Exception as e:
            logger.error(f"고정밀도 검색 오류: {e}", exc_info=True)
            raise SearchError(f"고정밀도 검색 중 오류가 발생했습니다: {str(e)}", original_exception=e)
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
            raise DatabaseError(f"판례 상세 조회 중 데이터베이스 오류가 발생했습니다: {str(e)}", original_exception=e)
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise SearchError(f"판례 상세 조회 중 예상치 못한 오류가 발생했습니다: {str(e)}", original_exception=e)
        finally:
            if conn:
                conn.close()

    def _rerank_cases(self, query: str, initial_results: list[dict], requested_size: int = 10) -> list[dict]:
        """
        Cross-encoder 모델을 사용하여 초기 검색 결과를 재평가하고 키워드 매칭으로 부스팅하여 관련도 순으로 재정렬한다.
        
        Args:
            query: 검색 쿼리
            initial_results: 초기 검색 결과
            requested_size: 사용자가 요청한 결과 개수
            
        Returns:
            재정렬된 결과 리스트 (requested_size 만큼)
        """
        if not initial_results:
            return []

        # 1. Cross-encoder 점수 계산
        documents_to_rerank = []
        for i, doc in enumerate(initial_results):
            # 제목 + 카테고리 + chunk_text를 조합하여 더 풍부한 컨텍스트 제공
            title = doc.get('title', '') or ''
            category = doc.get('category', '') or ''
            chunk_text = doc.get('chunk_text', '') or ''
            issue = doc.get('issue', '') or ''
            
            # 제목과 카테고리를 우선시하고 chunk_text를 보조로 사용
            combined_text = f"{title} {category} {issue} {chunk_text}".strip()
            documents_to_rerank.append(combined_text)

        scores = self.cross_encoder_model.get_cross_encoder_scores(query, documents_to_rerank)

        # 2. 키워드 매칭 부스팅 적용
        query_keywords = query.lower().split()
        scored_results = []
        
        for i, doc in enumerate(initial_results):
            base_score = scores[i]
            
            # 키워드 매칭 보너스 계산
            title = (doc.get('title', '') or '').lower()
            category = (doc.get('category', '') or '').lower()
            
            keyword_boost = 0.0
            
            # 제목에 키워드가 포함된 경우 큰 보너스
            for keyword in query_keywords:
                if keyword in title:
                    keyword_boost += 0.3
                if keyword in category:
                    keyword_boost += 0.2
            
            # 특별 키워드 추가 부스팅 (법률 용어)
            special_keywords = {
                '횡령': ['횡령', '배임'],
                '사기': ['사기', '편취'],
                '교통사고': ['교통사고', '교통'],
                '손해배상': ['손해배상', '배상'],
                '계약': ['계약', '약정'],
                '이혼': ['이혼', '혼인'],
                '상속': ['상속', '유산']
            }
            
            for main_keyword, related_keywords in special_keywords.items():
                if main_keyword in query.lower():
                    for related in related_keywords:
                        if related in title or related in category:
                            keyword_boost += 0.4
                            break
            
            # 최종 점수 = Cross-encoder 점수 + 키워드 부스팅
            final_score = base_score + keyword_boost
            
            doc['score'] = final_score
            doc['base_score'] = base_score  # 디버깅용
            doc['keyword_boost'] = keyword_boost  # 디버깅용
            scored_results.append(doc)

        reranked_results = sorted(scored_results, key=lambda x: x['score'], reverse=True)
        
        # 사용자가 요청한 개수만큼 반환
        actual_return_size = min(requested_size, len(reranked_results))
        top_results = reranked_results[:actual_return_size]
        
        # 디버깅 로그 개선
        logger.info(f"Reranked {len(reranked_results)} cases with keyword boosting, returning top {len(top_results)} (requested: {requested_size})")
        if top_results:
            logger.info(f"Top result: '{top_results[0].get('title', 'N/A')}' (score: {top_results[0]['score']:.3f} = base: {top_results[0]['base_score']:.3f} + boost: {top_results[0]['keyword_boost']:.3f})")
        
        return top_results
