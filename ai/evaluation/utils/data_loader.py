"""
평가 데이터 로딩 및 검증 모듈
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class EvalDataLoader:
    """평가 데이터 로더"""
    
    def __init__(self, eval_file_path: str):
        self.eval_file_path = Path(eval_file_path)
        self._validate_file_path()
    
    def _validate_file_path(self):
        """파일 경로 검증"""
        if not self.eval_file_path.exists():
            raise FileNotFoundError(f"평가 데이터 파일을 찾을 수 없습니다: {self.eval_file_path}")
        
        if not self.eval_file_path.suffix.lower() == '.json':
            raise ValueError(f"JSON 파일이 아닙니다: {self.eval_file_path}")
    
    def load_eval_data(self) -> List[Dict[str, Any]]:
        """평가 데이터 로딩"""
        try:
            with open(self.eval_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"평가 데이터 로딩 완료: {len(data)}개 케이스")
            
            # 데이터 구조 검증
            validated_data = self._validate_data_structure(data)
            return validated_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        except Exception as e:
            raise RuntimeError(f"데이터 로딩 중 오류 발생: {e}")
    
    def _validate_data_structure(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """데이터 구조 검증"""
        if not isinstance(data, list):
            raise ValueError("평가 데이터는 리스트 형태여야 합니다")
        
        validated_cases = []
        for i, case in enumerate(data):
            try:
                validated_case = self._validate_case_structure(case, i)
                validated_cases.append(validated_case)
            except Exception as e:
                logger.warning(f"케이스 {i} 검증 실패: {e}")
                continue
        
        if not validated_cases:
            raise ValueError("유효한 평가 케이스가 없습니다")
        
        logger.info(f"검증 완료: {len(validated_cases)}/{len(data)}개 케이스")
        return validated_cases
    
    def _validate_case_structure(self, case: Dict[str, Any], index: int) -> Dict[str, Any]:
        """개별 케이스 구조 검증"""
        required_fields = ['id', 'query_case', 'gold']
        
        for field in required_fields:
            if field not in case:
                raise ValueError(f"필수 필드 누락: {field}")
        
        # query_case 검증
        query_case = case['query_case']
        query_required_fields = ['title', 'summary', 'fullText']
        for field in query_required_fields:
            if field not in query_case or not query_case[field].strip():
                raise ValueError(f"query_case.{field} 필드가 비어있습니다")
        
        # gold 데이터 검증
        gold = case['gold']
        gold_required_fields = ['must_cite_cases', 'expected_sentence']
        for field in gold_required_fields:
            if field not in gold:
                raise ValueError(f"gold.{field} 필드가 누락되었습니다")
        
        # must_cite_cases는 리스트여야 함
        if not isinstance(gold['must_cite_cases'], list):
            raise ValueError("gold.must_cite_cases는 리스트여야 합니다")
        
        return case
    
    def get_case_by_id(self, data: List[Dict[str, Any]], case_id: str) -> Optional[Dict[str, Any]]:
        """ID로 특정 케이스 검색"""
        for case in data:
            if case.get('id') == case_id:
                return case
        return None
    
    def filter_by_category(self, data: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """카테고리별 케이스 필터링"""
        return [case for case in data if case.get('category') == category]
    
    def get_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """데이터 통계 정보"""
        categories = {}
        total_must_cite_cases = 0
        
        for case in data:
            category = case.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            must_cite_cases = case.get('gold', {}).get('must_cite_cases', [])
            total_must_cite_cases += len(must_cite_cases)
        
        return {
            'total_cases': len(data),
            'categories': categories,
            'avg_must_cite_cases': total_must_cite_cases / len(data) if data else 0
        }