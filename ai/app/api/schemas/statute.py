"""
법령 관련 스키마 정의
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class StatuteReference(BaseModel):
    """법령 참조 정보"""
    code: str = Field(..., description="법령명 (예: 형법, 민법)")
    articles: List[str] = Field(default_factory=list, description="관련 조항 목록 (예: ['347조(사기)', '350조(공갈)'])")
    description: str = Field("", description="법령 설명")
    statute_id: Optional[str] = Field(None, description="법령 ID")
    department: Optional[str] = Field(None, description="소관부처")

class LegacyStatuteReference(BaseModel):
    """기존 호환성을 위한 법령 참조 (article 단수형)"""
    code: str = Field(..., description="법령명")
    article: str = Field("", description="관련 조항")
    
    def to_new_format(self) -> StatuteReference:
        """새로운 형식으로 변환"""
        articles = [self.article] if self.article else []
        return StatuteReference(
            code=self.code,
            articles=articles
        )