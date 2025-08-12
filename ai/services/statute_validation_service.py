"""
법령 검증 및 보강 서비스
RAG에서 추출된 법령 정보를 검증하고 정확한 법령 정보로 보강
"""

import re
import psycopg2
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass
from difflib import SequenceMatcher
import uuid
import json

from config.settings import get_database_settings
from llm.models.embedding_model import EmbeddingModel
from utils.logger import LoggerMixin

@dataclass
class StatuteMatch:
    """법령 매칭 결과"""
    original_text: str
    matched_statute_id: Optional[str] = None
    statute_name: Optional[str] = None
    department: Optional[str] = None
    statute_type: Optional[str] = None
    description: Optional[str] = None
    confidence_score: float = 0.0
    validation_result: str = "not_found"  # matched, corrected, removed, suggested
    suggested_statute_id: Optional[str] = None
    error_type: Optional[str] = None  # not_found, typo, outdated

@dataclass
class EnhancedStatute:
    """보강된 법령 정보"""
    code: str
    articles: List[str]
    description: str
    statute_id: str
    department: str
    confidence: float

class StatuteValidationService(LoggerMixin):
    def __init__(self):
        self.db_settings = get_database_settings()
        self.embedding_model = EmbeddingModel()
        self.session_id = str(uuid.uuid4())
        
        # 법령 매칭 임계값
        self.CONFIDENCE_THRESHOLD = 0.60
        self.SIMILARITY_THRESHOLD = 0.40
        
    def _connect_db(self):
        """데이터베이스 연결"""
        return psycopg2.connect(
            host=self.db_settings.host,
            port=self.db_settings.port,
            database=self.db_settings.name,
            user=self.db_settings.user,
            password=self.db_settings.password
        )
    
    def parse_statutes_text(self, statutes_text: str) -> List[Dict[str, str]]:
        """
        RAG에서 추출된 statutes 문자열을 파싱하여 개별 법령 리스트로 변환
        
        예: "형법 제347조(사기), 민법 제750조(불법행위)" 
        → [{"code": "형법", "article": "제347조(사기)"}, {"code": "민법", "article": "제750조(불법행위)"}]
        """
        statutes = []
        
        if not statutes_text or statutes_text.strip() == "":
            return statutes
            
        # 쉼표, 세미콜론으로 분리
        statute_items = re.split(r'[,;]\s*', statutes_text.strip())
        
        for item in statute_items:
            item = item.strip()
            if not item:
                continue
                
            # 법령명과 조항 분리 패턴 매칭
            # 예: "형법 제347조(사기)", "민법 제750조", "상법", "형법 347조" 등
            patterns = [
                r'^(.+?)\s+(제?\d+조(?:\(\w+\))?)',  # "형법 제347조(사기)"
                r'^(.+?)\s+(\d+조(?:\(\w+\))?)',    # "형법 347조(사기)"  
                r'^(.+?)$'                         # "형법" (조항 없음)
            ]
            
            matched = False
            for pattern in patterns:
                match = re.match(pattern, item)
                if match:
                    if len(match.groups()) == 2:
                        code, article = match.groups()
                        statutes.append({
                            "code": code.strip(),
                            "article": article.strip(),
                            "original_text": item
                        })
                    else:
                        statutes.append({
                            "code": match.group(1).strip(),
                            "article": "",
                            "original_text": item
                        })
                    matched = True
                    break
            
            if not matched:
                # 패턴에 맞지 않는 경우 전체를 법령명으로 처리
                statutes.append({
                    "code": item,
                    "article": "",
                    "original_text": item
                })
        
        self.logger.debug(f"파싱된 법령: {statutes}")
        return statutes
    
    def search_statute_by_vector(self, query_text: str, limit: int = 5) -> List[Dict]:
        """벡터 검색으로 유사한 법령 찾기"""
        try:
            # 쿼리 텍스트 임베딩
            query_embedding = self.embedding_model.get_embedding(query_text)
            
            conn = self._connect_db()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            statute_id, statute_name, dept_name, statute_type_name,
                            description, 1 - (embedding <=> %s::vector) as similarity
                        FROM legal_statutes 
                        WHERE 1 - (embedding <=> %s::vector) > %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, query_embedding, self.SIMILARITY_THRESHOLD, query_embedding, limit))
                    
                    results = []
                    for row in cur.fetchall():
                        results.append({
                            'statute_id': row[0],
                            'statute_name': row[1],
                            'dept_name': row[2],
                            'statute_type_name': row[3],
                            'description': row[4],
                            'similarity': float(row[5])
                        })
                    
                    return results
                    
            finally:
                conn.close()
                
        except Exception as e:
            self.logger.error(f"벡터 검색 오류: {e}")
            return []
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (문자열 매칭)"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def validate_single_statute(self, statute: Dict[str, str]) -> StatuteMatch:
        """개별 법령 검증"""
        original_text = statute['original_text']
        code = statute['code']
        
        self.logger.debug(f"법령 검증 시작: {original_text}")
        
        # 1. 법령명에서 핵심 키워드 추출 (조항 정보 제거)
        # 예: "형법 제347조" -> "형법"
        clean_code = code.split()[0] if ' ' in code else code
        
        # 2. 벡터 검색으로 유사한 법령 찾기 (핵심 키워드로)
        search_results = self.search_statute_by_vector(clean_code, limit=10)
        
        # 3. 원본 코드로도 검색해보기 (추가 검색)
        if not search_results and code != clean_code:
            search_results = self.search_statute_by_vector(code, limit=10)
        
        if not search_results:
            return StatuteMatch(
                original_text=original_text,
                validation_result="removed",
                error_type="not_found",
                confidence_score=0.0
            )
        
        # 4. 가장 유사한 법령 찾기
        best_match = None
        best_score = 0.0
        
        for result in search_results:
            # 벡터 유사도와 텍스트 유사도 결합
            vector_similarity = result['similarity']
            
            # 핵심 키워드와 정확 매칭 확인
            statute_name = result['statute_name']
            text_similarity = max(
                self.calculate_text_similarity(clean_code, statute_name),
                self.calculate_text_similarity(code, statute_name)
            )
            
            # 정확한 법령명 매칭 시 보너스
            if clean_code == statute_name or code == statute_name:
                text_similarity = 1.0
            
            # 가중 평균 (벡터 유사도 60%, 텍스트 유사도 40%)
            combined_score = vector_similarity * 0.6 + text_similarity * 0.4
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = result
        
        if not best_match or best_score < self.CONFIDENCE_THRESHOLD:
            # 임계값 미달 시 제안만 제공
            suggestion = search_results[0] if search_results else None
            return StatuteMatch(
                original_text=original_text,
                validation_result="suggested" if suggestion else "removed",
                suggested_statute_id=suggestion['statute_id'] if suggestion else None,
                error_type="low_confidence",
                confidence_score=best_score
            )
        
        # 3. 매칭 성공
        validation_result = "matched" if best_score > 0.95 else "corrected"
        
        return StatuteMatch(
            original_text=original_text,
            matched_statute_id=best_match['statute_id'],
            statute_name=best_match['statute_name'],
            department=best_match['dept_name'],
            statute_type=best_match['statute_type_name'],
            description=best_match['description'],
            confidence_score=best_score,
            validation_result=validation_result,
            error_type="typo" if validation_result == "corrected" else None
        )
    
    def validate_statutes(self, statutes_text: str) -> List[StatuteMatch]:
        """RAG에서 추출된 법령들을 일괄 검증"""
        self.logger.info(f"법령 검증 시작: {statutes_text}")
        
        # 1. 문자열 파싱
        parsed_statutes = self.parse_statutes_text(statutes_text)
        
        if not parsed_statutes:
            self.logger.warning("파싱된 법령이 없습니다.")
            return []
        
        # 2. 각 법령을 검증
        validation_results = [
            self.validate_single_statute(statute) 
            for statute in parsed_statutes
        ]
        
        # 3. 결과 처리 완료
        
        self.logger.info(f"법령 검증 완료: {len(validation_results)}개 처리")
        return validation_results
    
    def enhance_statutes_response(self, validation_results: List[StatuteMatch], 
                                 original_statutes: List[Dict]) -> List[EnhancedStatute]:
        """검증 결과를 바탕으로 응답 형식에 맞는 법령 정보 생성"""
        enhanced_statutes = []
        
        # 원본 statutes에서 articles 정보 추출을 위한 매핑
        article_mapping = {}
        for statute in original_statutes:
            if 'article' in statute and statute['article']:
                article_mapping[statute.get('code', '')] = statute['article']
        
        for result in validation_results:
            # 법령이 매칭된 경우만 포함 (조항 유무와 관계없이)
            if result.validation_result in ['matched', 'corrected'] and result.matched_statute_id:
                
                # 원본에서 해당 법령의 조항 정보 찾기
                articles = []
                original_text = result.original_text
                
                # 법령명은 매칭된 정확한 이름 사용
                statute_code = result.statute_name
                
                # 조항 패턴 매칭 (제N조, N조 등)
                article_patterns = [
                    r'(제?\d+조(?:\([^)]+\))?)',  # 제347조(사기) 또는 347조
                    r'(제?\d+조의?\d*)',          # 제347조의2
                    r'(제?\d+조)',               # 제347조 또는 347조
                ]
                
                for pattern in article_patterns:
                    matches = re.findall(pattern, original_text)
                    for match in matches:
                        # 조항에서 괄호와 내용 제거 (예: "347조(사기)" -> "347조")
                        clean_article = match.split('(')[0] if '(' in match else match
                        if clean_article not in articles:  # 중복 방지
                            articles.append(clean_article)
                
                # 조항이 없으면 빈 배열
                if not articles:
                    articles = []
                
                enhanced_statute = EnhancedStatute(
                    code=statute_code,
                    articles=articles,
                    description=result.description or "",
                    statute_id=result.matched_statute_id,
                    department=result.department or "",
                    confidence=result.confidence_score
                )
                
                enhanced_statutes.append(enhanced_statute)
        
        return enhanced_statutes
    


# 사용 예시 및 테스트용 함수들
def test_statute_validation():
    """법령 검증 서비스 테스트"""
    service = StatuteValidationService()
    
    # 테스트 케이스
    test_cases = [
        "형법 제347조(사기)",
        "형사법 제123조",  # 존재하지 않는 법령
        "형볍 제347조",    # 오타
        "민법, 상법",      # 조항 없음
        "형법 제347조, 민법 제750조, 존재하지않는법 제999조"
    ]
    
    for test_case in test_cases:
        print(f"\n=== 테스트: {test_case} ===")
        results = service.validate_statutes(test_case)
        
        for result in results:
            print(f"원본: {result.original_text}")
            print(f"결과: {result.validation_result}")
            print(f"매칭: {result.statute_name}")
            print(f"신뢰도: {result.confidence_score:.3f}")
            print("---")

if __name__ == "__main__":
    test_statute_validation()