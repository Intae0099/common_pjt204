"""
공통 API 응답 모델
"""
from typing import Generic, TypeVar, Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """기본 API 응답 모델"""
    success: bool = Field(True, description="요청 성공 여부")
    data: Optional[T] = Field(None, description="응답 데이터")
    message: Optional[str] = Field(None, description="응답 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    success: bool = Field(False, description="요청 성공 여부")
    error: Dict[str, Any] = Field(..., description="에러 정보")
    message: str = Field(..., description="에러 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답 모델"""
    success: bool = Field(True, description="요청 성공 여부")
    data: List[T] = Field(..., description="응답 데이터 목록")
    total: int = Field(..., description="전체 데이터 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")
    message: Optional[str] = Field(None, description="응답 메시지")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")
    
    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        page: int,
        size: int,
        message: Optional[str] = None
    ):
        """페이지네이션 응답 생성"""
        pages = (total + size - 1) // size  # 올림 계산
        return cls(
            data=data,
            total=total,
            page=page,
            size=size,
            pages=pages,
            message=message
        )


def success_response(
    data: Optional[T] = None,
    message: Optional[str] = None
) -> BaseResponse[T]:
    """성공 응답 생성 헬퍼"""
    return BaseResponse(
        success=True,
        data=data,
        message=message
    )


def error_response(
    message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """에러 응답 생성 헬퍼"""
    return ErrorResponse(
        message=message,
        error=error_details or {}
    )


def paginated_response(
    data: List[T],
    total: int,
    page: int,
    size: int,
    message: Optional[str] = None
) -> PaginatedResponse[T]:
    """페이지네이션 응답 생성 헬퍼"""
    return PaginatedResponse.create(
        data=data,
        total=total,
        page=page,
        size=size,
        message=message
    )