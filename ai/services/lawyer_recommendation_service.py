"""
변호사 추천 서비스
"""
from typing import List, Dict, Optional

from services.external_api_client import ExternalAPIClient
from utils.logger import LoggerMixin
from utils.exceptions import handle_service_exceptions


class LawyerRecommendationService(LoggerMixin):
    """변호사 추천 서비스"""
    
    def __init__(self, external_api_client: ExternalAPIClient):
        """
        Args:
            external_api_client: 외부 API 클라이언트
        """
        self.external_api_client = external_api_client
        self.logger.info("LawyerRecommendationService initialized")
    
    @handle_service_exceptions("변호사 추천 중 오류가 발생했습니다.")
    async def get_lawyer_recommendations_from_tags(
        self, 
        tags: List[str],
        limit: int = 3
    ) -> Dict:
        """
        태그 리스트를 기반으로 변호사를 추천합니다.
        
        Args:
            tags: 전문 분야 태그 리스트 (CoT 프롬프트에서 추출된 태그들)
            limit: 추천할 변호사 수
            
        Returns:
            변호사 추천 결과
            {
                "extracted_tags": ["태그1", "태그2", "태그3"],
                "tag_ids": [1, 2, 3],
                "recommended_lawyers": [...]
            }
        """
        self.logger.info(f"Getting lawyer recommendations from tags: {tags}")
        
        if not tags:
            self.logger.warning("No tags provided, returning empty recommendations")
            return {
                "extracted_tags": [],
                "tag_ids": [],
                "recommended_lawyers": []
            }
        
        try:
            # 1. 태그 → tagIds 변환
            tag_ids = await self.external_api_client.resolve_tag_ids(tags)
            
            # 2. 변호사 추천
            lawyer_data = await self.external_api_client.recommend_lawyers(tag_ids, limit)
            
            # 3. 결과 통합
            result = {
                "extracted_tags": tags,
                "tag_ids": tag_ids,
                "recommended_lawyers": lawyer_data.get("recommendedLawyerList", [])
            }
            
            self.logger.info(f"Successfully generated lawyer recommendations: {len(result['recommended_lawyers'])} lawyers")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in lawyer recommendation process: {e}")
            raise