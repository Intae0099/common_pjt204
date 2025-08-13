"""
RAG 평가 메트릭 계산 모듈
"""
import logging
from typing import List, Dict, Any, Set
import re

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """RAG 평가 메트릭 계산기"""
    
    def __init__(self, k_values: List[int] = None):
        self.k_values = k_values or [1, 3, 5]
    
    def calculate_search_metrics(self, 
                               gold_cases: List[str], 
                               retrieved_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """검색 성능 메트릭 계산"""
        if not gold_cases or not retrieved_results:
            return self._empty_search_metrics()
        
        # 금본 답안 케이스 ID 집합
        gold_set = set(gold_cases)
        
        # 검색된 케이스 ID 리스트 (순서 유지)
        retrieved_ids = [result.get('case_id') for result in retrieved_results if result.get('case_id')]
        
        metrics = {}
        
        # K별 메트릭 계산
        for k in self.k_values:
            top_k_ids = retrieved_ids[:k]
            top_k_set = set(top_k_ids)
            
            # Recall@K = 상위 K개 중 정답 판례 수 / 전체 정답 판례 수
            recall_k = len(gold_set & top_k_set) / len(gold_set)
            metrics[f'recall@{k}'] = recall_k
            
            # Precision@K = 상위 K개 중 정답 판례 수 / K
            precision_k = len(gold_set & top_k_set) / k if k > 0 else 0.0
            metrics[f'precision@{k}'] = precision_k
        
        # MRR (Mean Reciprocal Rank) 계산
        mrr = self._calculate_mrr(gold_set, retrieved_ids)
        metrics['mrr'] = mrr
        
        return metrics
    
    def _calculate_mrr(self, gold_set: Set[str], retrieved_ids: List[str]) -> float:
        """MRR 계산: 첫 번째 정답의 순위 역수"""
        for rank, case_id in enumerate(retrieved_ids, 1):
            if case_id in gold_set:
                return 1.0 / rank
        return 0.0
    
    def _empty_search_metrics(self) -> Dict[str, float]:
        """빈 검색 메트릭 반환"""
        metrics = {}
        for k in self.k_values:
            metrics[f'recall@{k}'] = 0.0
            metrics[f'precision@{k}'] = 0.0
        metrics['mrr'] = 0.0
        return metrics
    
    def calculate_analysis_metrics(self, 
                                 gold_data: Dict[str, Any], 
                                 prediction: Dict[str, Any]) -> Dict[str, float]:
        """분석 성능 메트릭 계산"""
        metrics = {}
        
        # Citation Accuracy 계산
        metrics['citation_accuracy'] = self._calculate_citation_accuracy(
            gold_data.get('must_cite_cases', []),
            prediction
        )
        
        # Sentence Prediction Accuracy 계산
        metrics['sentence_prediction_accuracy'] = self._calculate_sentence_accuracy(
            gold_data.get('expected_sentence', ''),
            prediction.get('expected_sentence', '')
        )
        
        # Tag F1 Score 계산 (선택적)
        if 'tags' in gold_data and 'tags' in prediction:
            metrics['tag_f1'] = self._calculate_tag_f1(
                gold_data.get('tags', []),
                prediction.get('tags', [])
            )
        
        # Statute Relevance Score 계산 (선택적)
        if 'statutes' in gold_data and 'statutes' in prediction:
            metrics['statute_relevance'] = self._calculate_statute_relevance(
                gold_data.get('statutes', []),
                prediction.get('statutes', [])
            )
        
        return metrics
    
    def _calculate_citation_accuracy(self, 
                                   gold_citations: List[str], 
                                   prediction: Dict[str, Any]) -> float:
        """인용 정확도 계산"""
        if not gold_citations:
            return 1.0  # 정답이 없으면 완벽하다고 가정
        
        # 예측에서 인용된 판례 추출
        predicted_citations = self._extract_citations_from_prediction(prediction)
        
        gold_set = set(gold_citations)
        pred_set = set(predicted_citations)
        
        # 정확히 인용된 판례 수 / 전체 필수 인용 판례 수
        correct_citations = len(gold_set & pred_set)
        total_required = len(gold_set)
        
        return correct_citations / total_required if total_required > 0 else 1.0
    
    def _extract_citations_from_prediction(self, prediction: Dict[str, Any]) -> List[str]:
        """예측 결과에서 판례 인용 추출"""
        citations = []
        
        # references에서 추출
        references = prediction.get('references', {})
        if 'cases' in references:
            cases = references['cases']
            if isinstance(cases, list):
                for case in cases:
                    if isinstance(case, dict) and 'case_id' in case:
                        citations.append(case['case_id'])
                    elif isinstance(case, str):
                        citations.append(case)
        
        # opinion 텍스트에서 판례 번호 패턴 추출
        opinion = prediction.get('opinion', '')
        if opinion:
            case_pattern = r'\\b\\d{4}[가-힣]+\\d+\\b'
            matches = re.findall(case_pattern, opinion)
            citations.extend(matches)
        
        return list(set(citations))  # 중복 제거
    
    def _calculate_sentence_accuracy(self, gold_sentence: str, pred_sentence: str) -> float:
        """
        근거 기반 예상 판결 정확도 계산 (개선된 버전)
        - 기존: 단순 문자열 매칭
        - 개선: 근거 포함 여부, 추측성 표현, 핵심 결론 추출하여 비교
        """
        if not gold_sentence.strip():
            return 1.0
        
        gold_clean = gold_sentence.lower().strip()
        pred_clean = pred_sentence.lower().strip()
        
        # 1. 완전 일치 검사 (기존)
        if gold_clean == pred_clean:
            return 1.0
        
        # 2. 근거 기반 예측 점수 계산 (새로운 요구사항 반영)
        evidence_score = self._calculate_evidence_based_score(gold_clean, pred_clean)
        if evidence_score >= 0.85:  # 근거 기반 예측 정확도가 높으면 정답 인정
            return 1.0
        
        # 3. 핵심 결론 추출 및 비교
        gold_conclusion = self._extract_core_conclusion(gold_clean)
        pred_conclusion = self._extract_core_conclusion(pred_clean)
        
        if gold_conclusion and pred_conclusion:
            conclusion_similarity = self._calculate_legal_semantic_similarity(gold_conclusion, pred_conclusion)
            if conclusion_similarity >= 0.8:
                return 1.0
        
        # 4. 기존 정규화된 비교 (하위 호환성)
        normalized_score = self._calculate_normalized_similarity(gold_clean, pred_clean)
        if normalized_score >= 0.9:
            return 1.0
        
        # 5. 부분 점수 반환 (최고 점수 채택)
        return max(evidence_score, conclusion_similarity if 'conclusion_similarity' in locals() else 0, normalized_score)
    
    def _calculate_normalized_similarity(self, gold: str, pred: str) -> float:
        """정규화된 문자열 유사도 계산 (순서, 형태 변화 고려)"""
        import re
        
        # 숫자와 단위 정규화 ("2년" vs "2 년" vs "이년")
        def normalize_text(text):
            # 공백 정규화
            text = re.sub(r'\s+', '', text)
            # 숫자 한글 변환 (간단한 경우만)
            text = text.replace('일', '1').replace('이', '2').replace('삼', '3')
            text = text.replace('사', '4').replace('오', '5').replace('육', '6')
            return text
        
        gold_norm = normalize_text(gold)
        pred_norm = normalize_text(pred)
        
        # 정규화 후 완전 일치
        if gold_norm == pred_norm:
            return 1.0
        
        # 정규화 후 포함 관계
        if gold_norm in pred_norm or pred_norm in gold_norm:
            return 0.9
        
        # 편집 거리 기반 유사도
        return self._calculate_edit_distance_similarity(gold_norm, pred_norm)
    
    def _calculate_legal_semantic_similarity(self, gold: str, pred: str) -> float:
        """법률 용어 의미적 유사성 계산"""
        # 법률 용어 동의어/유사어 매핑
        legal_synonyms = {
            '무죄': ['무죄', '무죄추정', '무죄판결', '면죄', '불기소'],
            '유죄': ['유죄', '유죄판결', '기소', '처벌'],
            '징역': ['징역', '금고', '실형', '형량', '선고'],
            '집행유예': ['집행유예', '유예', '선고유예', '집유'],
            '벌금': ['벌금', '과료', '금전적처벌', '범칙금'],
            '기각': ['기각', '각하', '패소', '인용불가'],
            '인용': ['인용', '승소', '받아들임', '채택'],
            '무효': ['무효', '취소', '파기', '폐지']
        }
        
        # 정답과 예측에서 법률 용어 추출
        gold_terms = self._extract_legal_terms(gold, legal_synonyms)
        pred_terms = self._extract_legal_terms(pred, legal_synonyms)
        
        if not gold_terms:
            return 0.0
        
        # 동일한 의미 그룹에 속하는 용어들의 매칭 비율
        matched_groups = 0
        for gold_group in gold_terms:
            if any(pred_group == gold_group for pred_group in pred_terms):
                matched_groups += 1
        
        return matched_groups / len(gold_terms)
    
    def _extract_legal_terms(self, text: str, synonym_dict: dict) -> list:
        """텍스트에서 법률 용어 그룹 추출"""
        found_groups = []
        for group_key, synonyms in synonym_dict.items():
            for synonym in synonyms:
                if synonym in text:
                    found_groups.append(group_key)
                    break  # 같은 그룹에서 여러 용어가 발견되어도 한 번만 카운트
        return found_groups
    
    def _calculate_edit_distance_similarity(self, str1: str, str2: str) -> float:
        """편집 거리 기반 유사도 계산"""
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        if not str1 or not str2:
            return 0.0
        
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(str1, str2)
        return (max_len - distance) / max_len
    
    def _calculate_tag_f1(self, gold_tags: List[str], pred_tags: List[str]) -> float:
        """태그 F1 점수 계산"""
        gold_set = set(gold_tags)
        pred_set = set(pred_tags)
        
        if not gold_set and not pred_set:
            return 1.0
        
        if not gold_set or not pred_set:
            return 0.0
        
        intersection = gold_set & pred_set
        precision = len(intersection) / len(pred_set)
        recall = len(intersection) / len(gold_set)
        
        if precision + recall == 0:
            return 0.0
        
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    
    def _calculate_statute_relevance(self, 
                                   gold_statutes: List[Dict[str, Any]], 
                                   pred_statutes: List[Dict[str, Any]]) -> float:
        """법령 관련성 점수 계산"""
        # 법령명과 조항을 튜플로 변환
        gold_pairs = set()
        for statute in gold_statutes:
            name = statute.get('name', '')
            article = statute.get('article', '')
            if name and article:
                gold_pairs.add((name, article))
        
        pred_pairs = set()
        for statute in pred_statutes:
            name = statute.get('name', '')
            article = statute.get('article', '')
            if name and article:
                pred_pairs.add((name, article))
        
        if not gold_pairs:
            return 1.0
        
        intersection = gold_pairs & pred_pairs
        return len(intersection) / len(gold_pairs)
    
    def calculate_overall_metrics(self, 
                                case_results: List[Dict[str, Any]], 
                                total_runtime: float) -> Dict[str, float]:
        """전체 성능 메트릭 계산"""
        if not case_results:
            return {
                'end_to_end_accuracy': 0.0,
                'average_latency_ms': 0.0,
                'total_runtime_s': total_runtime,
                'success_rate': 0.0
            }
        
        # End-to-End Accuracy: 모든 조건을 만족하는 케이스 비율
        successful_cases = 0
        total_latency = 0
        valid_latency_count = 0
        
        for result in case_results:
            # 검색과 분석이 모두 성공하고 주요 메트릭이 좋은 경우
            search_success = result.get('search_success', False)
            analysis_success = result.get('analysis_success', False)
            citation_found = result.get('citation_found', False)
            
            if search_success and analysis_success and citation_found:
                successful_cases += 1
            
            # 평균 응답 시간 계산
            latency = result.get('latency_ms')
            if latency is not None and latency > 0:
                total_latency += latency
                valid_latency_count += 1
        
        # 0으로 나누는 것 방지
        total_cases = len(case_results)
        end_to_end_accuracy = successful_cases / total_cases if total_cases > 0 else 0.0
        average_latency = total_latency / valid_latency_count if valid_latency_count > 0 else 0.0
        success_rate = sum(1 for r in case_results if r.get('analysis_success', False)) / total_cases if total_cases > 0 else 0.0
        
        return {
            'end_to_end_accuracy': end_to_end_accuracy,
            'average_latency_ms': average_latency,
            'total_runtime_s': total_runtime,
            'success_rate': success_rate
        }
    
    def aggregate_metrics(self, all_case_metrics: List[Dict[str, Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
        """케이스별 메트릭을 집계하여 평균 계산"""
        if not all_case_metrics:
            return {}
        
        aggregated = {}
        
        # 메트릭 카테고리별로 집계
        for category in ['search_metrics', 'analysis_metrics']:
            aggregated[category] = {}
            
            # 각 메트릭별 평균 계산
            metric_sums = {}
            metric_counts = {}
            
            for case_metrics in all_case_metrics:
                if category in case_metrics and isinstance(case_metrics[category], dict):
                    for metric_name, value in case_metrics[category].items():
                        if isinstance(value, (int, float)) and not (isinstance(value, float) and (value != value)):  # NaN 체크
                            if metric_name not in metric_sums:
                                metric_sums[metric_name] = 0.0
                                metric_counts[metric_name] = 0
                            
                            metric_sums[metric_name] += value
                            metric_counts[metric_name] += 1
            
            # 평균 계산 (0으로 나누는 것 방지)
            for metric_name in metric_sums:
                count = metric_counts[metric_name]
                if count > 0:
                    aggregated[category][metric_name] = metric_sums[metric_name] / count
                else:
                    aggregated[category][metric_name] = 0.0
        
        return aggregated
    
    def _calculate_evidence_based_score(self, gold_sentence: str, pred_sentence: str) -> float:
        """
        근거 기반 예측 점수 계산
        - 판례 인용 여부 확인
        - 추측성 표현 사용 여부 확인  
        - 근거와 결론의 논리적 연결성 평가
        """
        score = 0.0
        
        # 1. 판례 근거 포함 여부 (0.4점)
        evidence_score = self._check_evidence_inclusion(pred_sentence)
        score += evidence_score * 0.4
        
        # 2. 추측성 표현 사용 여부 (0.3점)
        prediction_tone_score = self._check_prediction_tone(pred_sentence) 
        score += prediction_tone_score * 0.3
        
        # 3. 핵심 결론 일치도 (0.3점)
        conclusion_match_score = self._check_conclusion_match(gold_sentence, pred_sentence)
        score += conclusion_match_score * 0.3
        
        return min(score, 1.0)  # 최대 1.0으로 제한
    
    def _check_evidence_inclusion(self, pred_sentence: str) -> float:
        """판례 근거 포함 여부 확인"""
        evidence_patterns = [
            r'판례\s*분석\s*결과',  # "판례 분석 결과"
            r'유사\s*판례',        # "유사 판례"
            r'\d{4}[가-힣]+\d+',   # "2020다12345" 등 사건번호
            r'법원은.*판시',       # "법원은 ... 판시"
            r'판결.*바',          # "판결한 바"
            r'선례.*따라',        # "선례에 따라"
        ]
        
        for pattern in evidence_patterns:
            if re.search(pattern, pred_sentence):
                return 1.0
        
        return 0.0
    
    def _check_prediction_tone(self, pred_sentence: str) -> float:
        """추측성 표현 사용 여부 확인"""
        prediction_patterns = [
            r'예상된다',
            r'예측된다', 
            r'것으로\s*보인다',
            r'것으로\s*판단된다',
            r'가능성이\s*있다',
            r'바람직하다',
            r'적절하다고\s*보인다'
        ]
        
        for pattern in prediction_patterns:
            if re.search(pattern, pred_sentence):
                return 1.0
        
        return 0.0
    
    def _check_conclusion_match(self, gold_sentence: str, pred_sentence: str) -> float:
        """핵심 결론 일치도 확인"""
        gold_conclusion = self._extract_core_conclusion(gold_sentence)
        pred_conclusion = self._extract_core_conclusion(pred_sentence)
        
        if not gold_conclusion or not pred_conclusion:
            return 0.5  # 결론을 추출할 수 없으면 중간 점수
        
        return self._calculate_legal_semantic_similarity(gold_conclusion, pred_conclusion)
    
    def _extract_core_conclusion(self, sentence: str) -> str:
        """문장에서 핵심 결론 추출"""
        # 법률 결론 키워드들
        conclusion_keywords = [
            '무죄', '유죄', '징역', '벌금', '집행유예', 
            '기각', '인용', '각하', '승소', '패소',
            '무효', '취소', '파기', '인정', '배상'
        ]
        
        # 키워드가 포함된 부분을 핵심 결론으로 추출
        for keyword in conclusion_keywords:
            if keyword in sentence:
                # 해당 키워드 주변 맥락 추출 (앞뒤 10글자)
                pattern = f'.{{0,10}}{keyword}.{{0,10}}'
                match = re.search(pattern, sentence)
                if match:
                    return match.group().strip()
        
        # 키워드가 없으면 문장 끝부분 반환 (결론은 보통 문장 끝에 위치)
        if len(sentence) > 20:
            return sentence[-20:].strip()
        
        return sentence.strip()