"""
RAG 평가를 위한 API 호출 래퍼 모듈
"""
import requests
import logging
import json
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger(__name__)

class ServiceCaller:
    """API 서비스 호출 래퍼"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # 공통 헤더 설정
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """API 요청 공통 처리 함수"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            latency = (time.time() - start_time) * 1000  # ms
            
            response.raise_for_status()
            
            result = response.json()
            result['_latency_ms'] = latency
            
            logger.debug(f"{method} {endpoint} - {response.status_code} ({latency:.1f}ms)")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"API 타임아웃: {method} {endpoint}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"API 연결 오류: {method} {endpoint}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 오류: {method} {endpoint} - {e}")
            raise
        except Exception as e:
            logger.error(f"API 호출 오류: {method} {endpoint} - {e}")
            raise
    
    def search_cases(self, query: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """검색 API 호출"""
        params = {
            'keyword': query,
            'page': page,
            'size': size
        }
        
        response = self._make_request('GET', '/api/search/cases', params=params)
        return response
    
    def analyze_case(self, case_data: Dict[str, Any], recommend_lawyers: bool = True) -> Dict[str, Any]:
        """사례 분석 API 호출"""
        
        # query_case를 case로 변환하여 API 요청 형식에 맞춤
        request_data = {
            'case': {
                'title': case_data.get('title', ''),
                'summary': case_data.get('summary', ''),
                'fullText': case_data.get('fullText', '')
            },
            'recommend_lawyers': recommend_lawyers
        }
        
        response = self._make_request('POST', '/api/analysis', json=request_data)
        return response
    
    def extract_search_results(self, search_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """검색 응답에서 결과 리스트 추출"""
        try:
            if not search_response.get('success', False):
                return []
            
            # API 응답 구조 확인: data가 리스트인지 dict인지 확인
            data = search_response.get('data', [])
            
            # data가 리스트인 경우 (실제 API 응답)
            if isinstance(data, list):
                items = data
            # data가 dict인 경우 (이전 예상 구조)
            elif isinstance(data, dict):
                items = data.get('items', [])
            else:
                logger.warning(f"예상치 못한 data 구조: {type(data)}")
                return []
            
            # 검색 결과를 평가용 형태로 변환
            results = []
            for idx, item in enumerate(items):
                # item이 dict인지 확인
                if not isinstance(item, dict):
                    logger.warning(f"검색 결과 item이 dict가 아님: {type(item)}, 값: {item}")
                    continue
                
                results.append({
                    'case_id': item.get('caseId'),
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'summary': item.get('summary'),
                    'rank': idx + 1  # 1부터 시작하는 순위
                })
            
            return results
            
        except Exception as e:
            logger.error(f"검색 결과 추출 오류: {e}")
            logger.error(f"응답 구조: {search_response}")
            return []
    
    def extract_analysis_result(self, analysis_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """분석 응답에서 결과 추출"""
        try:
            if not analysis_response.get('success', False):
                return None
            
            data = analysis_response.get('data', {})
            report = data.get('report', {})
            
            return {
                'issues': report.get('issues', []),
                'opinion': report.get('opinion', ''),
                'expected_sentence': report.get('expected_sentence', ''),
                'confidence': report.get('confidence', 0.0),
                'references': report.get('references', {}),
                'statutes': report.get('statutes', []),
                'tags': report.get('tags', []),
                'recommendedLawyers': report.get('recommendedLawyers', [])
            }
            
        except Exception as e:
            logger.error(f"분석 결과 추출 오류: {e}")
            return None
    
    def extract_cited_cases(self, analysis_result: Dict[str, Any]) -> List[str]:
        """분석 결과에서 인용된 판례 ID 추출"""
        cited_cases = []
        
        try:
            # references에서 판례 ID 추출
            references = analysis_result.get('references', {})
            
            # 여러 형태로 저장될 수 있는 판례 참조 처리
            if 'cases' in references:
                cases = references['cases']
                if isinstance(cases, list):
                    for case in cases:
                        if isinstance(case, dict) and 'case_id' in case:
                            cited_cases.append(case['case_id'])
                        elif isinstance(case, str):
                            cited_cases.append(case)
            
            # opinion 텍스트에서 판례 번호 패턴 추출 (예: 2021고합456)
            opinion = analysis_result.get('opinion', '')
            if opinion:
                import re
                case_pattern = r'\d{4}[가-힣]+\d+'
                matches = re.findall(case_pattern, opinion)
                cited_cases.extend(matches)
            
            # 중복 제거
            cited_cases = list(set(cited_cases))
            
        except Exception as e:
            logger.error(f"인용 판례 추출 오류: {e}")
        
        return cited_cases
    
    def health_check(self) -> bool:
        """API 서버 상태 확인"""
        try:
            response = self._make_request('GET', '/')
            return True
        except Exception as e:
            logger.error(f"헬스 체크 실패: {e}")
            return False