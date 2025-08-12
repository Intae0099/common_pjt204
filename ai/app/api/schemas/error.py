from enum import Enum
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """
    API 에러 코드
    """
    INVALID_PARAM = "INVALID_PARAM"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    SERVER_ERROR = "SERVER_ERROR"


class Error(BaseModel):
    code: ErrorCode = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")


DataT = TypeVar("DataT")


class BaseSuccessResponse(BaseModel, Generic[DataT]):
    success: bool = Field(True, description="성공 여부")
    data: DataT | None = Field(None, description="응답 데이터")


class BaseErrorResponse(BaseModel):
    success: bool = Field(False, description="성공 여부")
    error: Error = Field(..., description="에러 정보")
    details: Any | None = Field(None, description="상세 에러 정보 (개발용)")
