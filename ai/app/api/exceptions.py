from typing import Any

from app.api.schemas.error import ErrorCode


class APIException(Exception):
    """
    모든 API 예외의 기본 클래스
    """

    def __init__(
        self, code: ErrorCode, message: str, details: Any | None = None
    ) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class BadRequestException(APIException):
    """
    400 Bad Request
    """

    def __init__(
        self, message: str = "요청 파라미터가 잘못되었습니다.", details: Any | None = None
    ) -> None:
        super().__init__(ErrorCode.INVALID_PARAM, message, details)


class UnauthorizedException(APIException):
    """
    401 Unauthorized
    """

    def __init__(self, message: str = "인증에 실패했습니다.", details: Any | None = None) -> None:
        super().__init__(ErrorCode.UNAUTHORIZED, message, details)


class ResourceNotFoundException(APIException):
    """
    404 Not Found
    """

    def __init__(self, message: str = "리소스를 찾을 수 없습니다.", details: Any | None = None) -> None:
        super().__init__(ErrorCode.NOT_FOUND, message, details)
