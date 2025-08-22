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
        하이브리드 검색: 키워드 검색을 우선으로 하고 벡터 검색을 보조로 사용한다.
        벡터 검색 성능이 낮아 키워드 기반 검색을 메인으로 전환.
        """
        conn = None
        try:
            conn = get_psycopg2_connection()
            register_vector(conn)

            with conn.cursor() as cur:
                # 전체 개수 (키워드 기반)
                cur.execute("""
                    SELECT COUNT(DISTINCT lc.case_id) 
                    FROM legal_cases lc 
                    WHERE lc.title ILIKE %s OR lc.full_text ILIKE %s OR lc.category ILIKE %s
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                keyword_total = cur.fetchone()[0]

                # 1단계: 키워드 검색 (주력)
                keyword_size = min(size * 2, 30)  # 요청의 2배 또는 최대 30개
                cur.execute("""
                    SELECT lc.case_id, lc.title, lc.decision_date, lc.category, 
                           lc.issue, lc.summary, lc.full_text, lc.statutes,
                           '' as chunk_text,
                           CASE 
                               WHEN lc.title ILIKE %s THEN 3
                               WHEN lc.category ILIKE %s THEN 2  
                               ELSE 1
                           END as keyword_relevance
                    FROM legal_cases lc
                    WHERE lc.title ILIKE %s OR lc.full_text ILIKE %s OR lc.category ILIKE %s
                    ORDER BY keyword_relevance DESC, lc.decision_date DESC
                    LIMIT %s
                    """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', keyword_size))
                
                keyword_results = [
                    {
                        "case_id": cid,
                        "title": title,
                        "decision_date": decision_date,
                        "category": category,
                        "issue": issue,
                        "summary": summary,
                        "full_text": full_text,
                        "chunk_text": chunk_text,
                        "statutes": statutes,
                        "_source": "keyword"
                    }
                    for cid, title, decision_date, category, issue, summary, full_text, statutes, chunk_text, relevance in cur.fetchall()
                ]

                # 2단계: 키워드 결과가 부족하면 벡터 검색으로 보완
                initial_results = keyword_results
                if len(keyword_results) < size:
                    logger.info(f"키워드 검색 결과 부족 ({len(keyword_results)}개), 벡터 검색으로 보완...")
                    
                    query_embedding = self.embedding_model.get_embedding(query)
                    
                    # 키워드 검색에서 나온 case_id들 제외
                    exclude_ids = [r["case_id"] for r in keyword_results] if keyword_results else []
                    exclude_clause = ""
                    exclude_params = []
                    
                    if exclude_ids:
                        placeholders = ",".join(["%s"] * len(exclude_ids))
                        exclude_clause = f"AND lc.case_id NOT IN ({placeholders})"
                        exclude_params = exclude_ids
                    
                    vector_size = size - len(keyword_results)
                    vector_query = f"""
                        SELECT lc.case_id, lc.title, lc.decision_date, lc.category, 
                               lc.issue, lc.summary, lc.full_text, lch.chunk_text, lc.statutes
                        FROM legal_chunks lch
                        JOIN legal_cases lc ON lch.case_id = lc.case_id
                        WHERE 1=1 {exclude_clause}
                        ORDER BY lch.embedding <-> %s::vector
                        LIMIT %s
                    """
                    
                    cur.execute(vector_query, exclude_params + [query_embedding, vector_size])
                    
                    vector_results = [
                        {
                            "case_id": cid,
                            "title": title,
                            "decision_date": decision_date,
                            "category": category,
                            "issue": issue,
                            "summary": summary,
                            "full_text": full_text,
                            "chunk_text": chunk_text,
                            "statutes": statutes,
                            "_source": "vector"
                        }
                        for cid, title, decision_date, category, issue, summary, full_text, chunk_text, statutes in cur.fetchall()
                    ]
                    
                    initial_results.extend(vector_results)
                
                # 전체 count는 키워드 기반 + 벡터 전체를 합산 추정
                if keyword_total > 0:
                    total_count = keyword_total
                else:
                    cur.execute("SELECT COUNT(DISTINCT lc.case_id) FROM legal_chunks lch JOIN legal_cases lc ON lch.case_id = lc.case_id")
                    total_count = cur.fetchone()[0]

            # 🔧 DEBUG: 하이브리드 검색 결과 표시
            keyword_count = len([r for r in initial_results if r.get("_source") == "keyword"])
            vector_count = len([r for r in initial_results if r.get("_source") == "vector"])
            logger.info(f"[hybrid_search] total={len(initial_results)} (keyword={keyword_count}, vector={vector_count})")

            if use_rerank and len(initial_results) > 1:
                logger.info("Applying reranking to hybrid search results...")
                reranked = self._rerank_cases(query, initial_results, requested_size=size)

                # 디버그: 최종 결과 소스 분포
                final_keyword = len([r for r in reranked if r.get("_source") == "keyword"])
                final_vector = len([r for r in reranked if r.get("_source") == "vector"])
                logger.info(f"[final_results] total={len(reranked)} (keyword={final_keyword}, vector={final_vector})")

                return reranked, total_count
            else:
                logger.info("Reranking skipped or insufficient results.")
                # 요청된 개수만큼만 반환
                return initial_results[:size], total_count

        except psycopg2.Error as e:
            logger.error(f"데이터베이스 오류: {e}")
            raise DatabaseError(f"판례 검색 중 데이터베이스 오류가 발생했습니다: {str(e)}", original_exception=e)
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise SearchError(f"판례 검색 중 예상치 못한 오류가 발생했습니다: {str(e)}", original_exception=e)
        finally:
            if conn:
                conn.close()

    async def high_precision_search(self, query: str, top_k: int = 3) -> list[dict]:
        """
        AI 사전 상담용 고정밀도 검색
        3단계 필터링으로 최고 품질의 상위 k개 결과만 반환
        """
        conn = None
        try:
            conn = get_psycopg2_connection()
            register_vector(conn)

            with conn.cursor() as cur:
                # 1단계: 대량 후보 수집 (키워드 + 벡터)
                logger.info(f"[high_precision] 1단계: 대량 후보 수집 시작 (query: {query})")
                
                # 1-1. 키워드 검색 (40개)
                keyword_candidates = []
                cur.execute("""
                    SELECT DISTINCT lc.case_id, lc.title, lc.decision_date, lc.category, 
                           lc.issue, lc.summary, lc.full_text, lc.statutes,
                           CASE 
                               WHEN lc.title ILIKE %s THEN 5
                               WHEN lc.category ILIKE %s THEN 4
                               WHEN lc.issue ILIKE %s THEN 3
                               WHEN lc.summary ILIKE %s THEN 2
                               ELSE 1
                           END as keyword_score
                    FROM legal_cases lc
                    WHERE lc.title ILIKE %s OR lc.category ILIKE %s OR lc.issue ILIKE %s 
                       OR lc.summary ILIKE %s OR lc.full_text ILIKE %s
                    ORDER BY keyword_score DESC, lc.decision_date DESC
                    LIMIT 40
                    """, tuple([f'%{query}%'] * 9))
                
                for row in cur.fetchall():
                    keyword_candidates.append({
                        "case_id": row[0],
                        "title": row[1],
                        "decision_date": row[2],
                        "category": row[3],
                        "issue": row[4],
                        "summary": row[5],
                        "full_text": row[6],
                        "statutes": row[7],
                        "chunk_text": "",
                        "_source": "keyword",
                        "_score": row[8]
                    })
                
                # 1-2. 벡터 검색 (20개, 키워드 결과 제외)
                keyword_case_ids = [c["case_id"] for c in keyword_candidates]
                vector_candidates = []
                
                if len(keyword_case_ids) < 50:  # 키워드 결과가 충분하지 않으면 벡터로 보완
                    query_embedding = self.embedding_model.get_embedding(query)
                    
                    exclude_clause = ""
                    exclude_params = []
                    if keyword_case_ids:
                        placeholders = ",".join(["%s"] * len(keyword_case_ids))
                        exclude_clause = f"AND lc.case_id NOT IN ({placeholders})"
                        exclude_params = keyword_case_ids
                    
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
                    
                    cur.execute(vector_query, exclude_params + [query_embedding, query_embedding])
                    
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

                # 2단계: 정확도 필터링
                all_candidates = keyword_candidates + vector_candidates
                logger.info(f"[high_precision] 1단계 완료: {len(all_candidates)}개 후보 (keyword: {len(keyword_candidates)}, vector: {len(vector_candidates)})")
                
                if not all_candidates:
                    logger.warning("[high_precision] 후보가 없어 빈 결과 반환")
                    return []
                
                # 2단계: 관련성 점수 재계산 및 필터링
                logger.info("[high_precision] 2단계: 정확도 필터링 시작")
                
                filtered_candidates = []
                query_lower = query.lower()
                
                for candidate in all_candidates:
                    title = (candidate.get("title") or "").lower()
                    category = (candidate.get("category") or "").lower()
                    
                    # 관련성 점수 계산
                    relevance_score = 0.0
                    
                    # 직접 키워드 매칭
                    if query_lower in title:
                        relevance_score += 3.0
                    if query_lower in category:
                        relevance_score += 2.0
                    
                    # 법률 용어 특별 매칭
                    legal_term_map = {
                        "횡령": ["횡령", "배임", "특정경제범죄"],
                        "사기": ["사기", "편취", "기망"],
                        "교통사고": ["교통사고", "교통", "자동차"],
                        "손해배상": ["손해배상", "배상", "피해"],
                        "계약": ["계약", "약정", "합의"],
                        "이혼": ["이혼", "혼인", "가사"],
                        "상속": ["상속", "유산", "유언"]
                    }
                    
                    for main_term, related_terms in legal_term_map.items():
                        if main_term in query_lower:
                            for term in related_terms:
                                if term in title:
                                    relevance_score += 2.0
                                    break
                    
                    # 기본 점수 추가
                    relevance_score += candidate.get("_score", 0.0)
                    
                    # 최소 관련성 임계값 적용
                    if relevance_score >= 1.0:  # 최소 관련성 보장
                        candidate["_relevance"] = relevance_score
                        filtered_candidates.append(candidate)
                
                # 관련성 순으로 정렬
                filtered_candidates.sort(key=lambda x: x["_relevance"], reverse=True)
                
                # 상위 15개만 유지
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
                    # Cross-encoder로 최종 순위 결정
                    final_results = self._rerank_cases(query, filtered_candidates, requested_size=top_k)
                
                logger.info(f"[high_precision] 완료: {len(final_results)}개 반환")
                
                # 디버그 로그
                if final_results:
                    top_title = final_results[0].get("title", "N/A")
                    top_source = final_results[0].get("_source", "N/A")
                    top_relevance = final_results[0].get("_relevance", 0)
                    logger.info(f"[high_precision] Top result: '{top_title}' (source: {top_source}, relevance: {top_relevance:.2f})")
                
                return final_results

        except Exception as e:
            logger.error(f"고정밀도 검색 오류: {e}")
            import traceback
            traceback.print_exc()
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
