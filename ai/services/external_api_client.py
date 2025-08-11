"""
외부 백엔드 API 호출을 위한 클라이언트
"""
import httpx
from typing import List, Dict, Optional
from utils.logger import LoggerMixin
from utils.exceptions import handle_service_exceptions, APIError
from config.settings import get_api_settings


class ExternalAPIClient(LoggerMixin):
    """외부 백엔드 API 호출 클라이언트"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Args:
            base_url: API 기본 URL (기본값: 설정에서 가져옴)
        """
        self.base_url = base_url or get_api_settings().backend_api_url
        self.timeout = 30.0  # 30초 타임아웃
        self.logger.info(f"ExternalAPIClient initialized with base_url: {self.base_url}")
    
    async def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict] = None) -> Dict:
        """
        공통 HTTP 요청 메서드
        
        Args:
            method: HTTP 메서드 (POST, GET 등)
            endpoint: API 엔드포인트 (예: /api/tag/resolve)
            json_data: 요청 본문 데이터
            
        Returns:
            API 응답 데이터
            
        Raises:
            APIError: API 호출 실패 시
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        
        self.logger.info(f"Making {method} request to {url}")
        if json_data:
            self.logger.debug(f"Request data: {json_data}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    headers=headers
                )
                
                # 응답 로깅
                self.logger.info(f"Response status: {response.status_code}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                
                # HTTP 에러 체크
                if response.status_code >= 400:
                    error_text = response.text
                    self.logger.error(f"HTTP {response.status_code} error: {error_text}")
                    raise APIError(f"External API error: HTTP {response.status_code} - {error_text}")
                
                # JSON 응답 파싱
                response_data = response.json()
                self.logger.debug(f"Response data: {response_data}")
                
                return response_data
                
        except httpx.TimeoutException:
            self.logger.error(f"Request timeout for {url}")
            raise APIError("External API request timeout")
        except httpx.RequestError as e:
            self.logger.error(f"Request error for {url}: {e}")
            raise APIError(f"External API request failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error for {url}: {e}")
            raise APIError(f"Unexpected error in external API call: {e}")
    
    @handle_service_exceptions("태그 ID 해결 중 오류가 발생했습니다.")
    async def resolve_tag_ids(self, tags: List[str]) -> List[int]:
        """
        태그 문자열을 tagIds로 변환
        
        Args:
            tags: 태그 문자열 리스트 (예: ["무면허운전", "음주운전"])
            
        Returns:
            tagIds 리스트 (예: [2, 1])
            
        Raises:
            APIError: API 호출 실패 시
        """
        if not tags:
            self.logger.warning("Empty tags list provided")
            return []
        
        request_data = {"tags": tags}
        response = await self._make_request("POST", "/api/tag/resolve", request_data)
        
        # 응답 구조 검증
        if "data" not in response or "tagIds" not in response["data"]:
            self.logger.error(f"Invalid response structure: {response}")
            raise APIError("Invalid response structure from tag resolve API")
        
        tag_ids = response["data"]["tagIds"]
        self.logger.info(f"Successfully resolved {len(tags)} tags to {len(tag_ids)} tagIds")
        
        return tag_ids
    
    @handle_service_exceptions("변호사 추천 중 오류가 발생했습니다.")
    async def recommend_lawyers(self, tag_ids: List[int], limit: int = 3) -> Dict:
        """
        tagIds를 기반으로 변호사 추천
        
        Args:
            tag_ids: 태그 ID 리스트 (예: [2, 1, 8])
            limit: 추천할 변호사 수 (기본값: 3)
            
        Returns:
            추천 변호사 정보
            {
                "recommendedLawyerList": [
                    {
                        "lawyerId": 10,
                        "name": "제갈변호4",
                        "introduction": "교통사건 전문",
                        "tags": [1, 2, 4, 5]
                    },
                    ...
                ]
            }
            
        Raises:
            APIError: API 호출 실패 시
        """
        if not tag_ids:
            self.logger.warning("Empty tag_ids list provided")
            return {"recommendedLawyerList": []}
        
        request_data = {"tagIds": tag_ids, "limit": limit}
        response = await self._make_request("POST", "/api/tag/recommend", request_data)
        
        # 응답 구조 검증
        if "data" not in response or "recommendedLawyerList" not in response["data"]:
            self.logger.error(f"Invalid response structure: {response}")
            raise APIError("Invalid response structure from lawyer recommend API")
        
        lawyer_data = response["data"]
        lawyer_count = len(lawyer_data["recommendedLawyerList"])
        self.logger.info(f"Successfully received {lawyer_count} lawyer recommendations")
        
        return lawyer_data
    
    async def close(self):
        """리소스 정리 (필요시 호출)"""
        # httpx.AsyncClient는 컨텍스트 매니저로 사용하므로 별도 정리 불필요
        self.logger.info("ExternalAPIClient closed")