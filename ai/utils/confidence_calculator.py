from typing import List, Dict, Any
import numpy as np
from utils.logger import LoggerMixin


class ConfidenceCalculator(LoggerMixin):
    """
    판례 유사도, 사건 일치도 등 객관적 근거를 기반으로 신뢰도를 계산하는 클래스
    신뢰도 범위: 30% ~ 95%
    """
    
    def __init__(self):
        self.min_confidence = 0.30  # 하한선 30%
        self.max_confidence = 0.95  # 상한선 95%
    
    def calculate_confidence(
        self, 
        query_case: str, 
        retrieved_docs: List[Dict[str, Any]], 
        similarity_scores: List[float] = None
    ) -> float:
        """
        객관적 근거를 기반으로 신뢰도를 계산
        
        Args:
            query_case: 사용자 질문/사건
            retrieved_docs: 검색된 판례 문서들
            similarity_scores: 유사도 점수들 (옵션)
        
        Returns:
            float: 계산된 신뢰도 (0.30 ~ 0.95)
        """
        if not retrieved_docs:
            self.logger.warning("검색된 판례가 없어 최소 신뢰도 반환")
            return self.min_confidence
        
        try:
            # 1. 판례 유사도 기반 점수 (0-0.4)
            similarity_score = self._calculate_similarity_confidence(similarity_scores, retrieved_docs)
            
            # 2. 사건 유형 일치도 (0-0.3)
            case_match_score = self._calculate_case_match_confidence(query_case, retrieved_docs)
            
            # 3. 법령 적용 정확도 (0-0.25)
            statute_accuracy = self._calculate_statute_confidence(retrieved_docs)
            
            # 최종 신뢰도 계산
            raw_confidence = similarity_score + case_match_score + statute_accuracy
            
            # 기본 신뢰도 30%에 추가 점수 더하기
            final_confidence = self.min_confidence + (raw_confidence * (self.max_confidence - self.min_confidence))
            
            # 범위 제한 적용
            final_confidence = max(self.min_confidence, min(self.max_confidence, final_confidence))
            
            self.logger.info(f"신뢰도 계산 완료: 유사도={similarity_score:.3f}, 사건일치={case_match_score:.3f}, 법령정확도={statute_accuracy:.3f}, 최종={final_confidence:.3f}")
            
            return round(final_confidence, 3)
            
        except Exception as e:
            self.logger.error(f"신뢰도 계산 중 오류 발생: {e}")
            return self.min_confidence
    
    def _calculate_similarity_confidence(self, similarity_scores: List[float], retrieved_docs: List[Dict]) -> float:
        """판례 유사도 기반 신뢰도 점수 계산 (0-0.4)"""
        if not similarity_scores:
            # similarity_scores가 없는 경우 retrieved_docs에서 유사도 정보 추출 시도
            similarity_scores = []
            for doc in retrieved_docs[:5]:  # 상위 5개만 사용
                # _score 필드가 있으면 사용, 없으면 기본값
                score = doc.get('_score', 0.5)
                similarity_scores.append(score)
        
        if not similarity_scores:
            return 0.2  # 기본 점수
        
        # 상위 3개 판례의 평균 유사도 사용
        top_scores = sorted(similarity_scores, reverse=True)[:3]
        avg_similarity = np.mean(top_scores)
        
        # 유사도를 0-0.4 범위로 정규화
        # 일반적으로 elasticsearch 점수는 0-10 범위이므로 적절히 스케일링
        if avg_similarity > 10:
            avg_similarity = avg_similarity / 100  # 0-100 범위인 경우
        elif avg_similarity > 1:
            avg_similarity = avg_similarity / 10   # 0-10 범위인 경우
        
        similarity_confidence = min(0.4, avg_similarity * 0.4)
        return similarity_confidence
    
    def _calculate_case_match_confidence(self, query_case: str, retrieved_docs: List[Dict]) -> float:
        """사건 유형 일치도 기반 신뢰도 점수 계산 (0-0.3)"""
        if not query_case or not retrieved_docs:
            return 0.1
        
        # 간단한 키워드 매칭으로 사건 유형 일치도 계산
        query_keywords = self._extract_case_keywords(query_case.lower())
        
        match_scores = []
        for doc in retrieved_docs[:5]:  # 상위 5개 판례만 확인
            doc_text = ""
            if 'chunk_text' in doc:
                doc_text = doc['chunk_text'].lower()
            elif 'issue' in doc:
                doc_text = doc['issue'].lower()
            elif 'summary' in doc:
                doc_text = doc['summary'].lower()
            
            if doc_text:
                doc_keywords = self._extract_case_keywords(doc_text)
                match_ratio = self._calculate_keyword_match_ratio(query_keywords, doc_keywords)
                match_scores.append(match_ratio)
        
        if match_scores:
            avg_match = np.mean(match_scores)
            case_match_confidence = avg_match * 0.3
        else:
            case_match_confidence = 0.1
        
        return case_match_confidence
    
    def _calculate_statute_confidence(self, retrieved_docs: List[Dict]) -> float:
        """법령 적용 정확도 기반 신뢰도 점수 계산 (0-0.25)"""
        statute_info_count = 0
        total_docs = len(retrieved_docs[:5])  # 상위 5개만 확인
        
        for doc in retrieved_docs[:5]:
            # 법령 정보가 있는지 확인
            if any(field in doc for field in ['statutes', 'legal_basis', 'law_references']):
                statute_info_count += 1
        
        if total_docs > 0:
            statute_ratio = statute_info_count / total_docs
            statute_confidence = statute_ratio * 0.25
        else:
            statute_confidence = 0.1
        
        return statute_confidence
    
    def _extract_case_keywords(self, text: str) -> set:
        """사건에서 핵심 키워드 추출"""
        # 법률 관련 핵심 키워드들
        legal_keywords = [
            # 형사 관련
            '폭행', '상해', '사기', '절도', '강도', '살인', '성폭력', '횡령', '배임',
            '음주운전', '무면허', '교통사고', '뺑소니', '마약', '도박', '공갈', '협박',
            
            # 민사 관련  
            '손해배상', '계약', '임대차', '매매', '건축', '부동산', '상속', '이혼',
            '위자료', '임금', '퇴직금', '보험', '의료사고', '제조물책임',
            
            # 행정 관련
            '행정처분', '영업정지', '과태료', '행정심판', '정보공개', '건축허가',
            
            # 일반적 법률 용어
            '과실', '고의', '위법', '정당방위', '긴급피난', '승낙', '동의'
        ]
        
        found_keywords = set()
        for keyword in legal_keywords:
            if keyword in text:
                found_keywords.add(keyword)
        
        return found_keywords
    
    def _calculate_keyword_match_ratio(self, query_keywords: set, doc_keywords: set) -> float:
        """키워드 매칭 비율 계산"""
        if not query_keywords:
            return 0.0
        
        intersection = query_keywords.intersection(doc_keywords)
        union = query_keywords.union(doc_keywords)
        
        if not union:
            return 0.0
        
        # Jaccard 유사도 계산
        jaccard_similarity = len(intersection) / len(union)
        return jaccard_similarity