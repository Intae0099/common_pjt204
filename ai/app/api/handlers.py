import logging

from fastapi import Request, status
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

from app.api.exceptions import APIException
from app.api.schemas.error import BaseErrorResponse, Error, ErrorCode
from utils.exceptions import BaseServiceException, DatabaseError, LLMError, SearchError, ValidationError

logger = logging.getLogger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    커스텀 API 예외 핸들러
    """
    error = Error(code=exc.code, message=exc.message)
    status_code = status.HTTP_400_BAD_REQUEST
    if exc.code == ErrorCode.NOT_FOUND:
        status_code = status.HTTP_404_NOT_FOUND

    logger.warning(f"API Exception: {exc.code} - {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=status_code,
        content=BaseErrorResponse(error=error, details=exc.details).model_dump(
            exclude_none=True
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Pydantic 유효성 검사 예외 핸들러
    RequestValidationError를 400/INVALID_PARAM으로 변환
    """
    error = Error(
        code=ErrorCode.INVALID_PARAM, message="요청 파라미터가 잘못되었습니다."
    )
    logger.warning(
        f"Validation Error: {exc.errors()}", extra={"body": exc.body}
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=BaseErrorResponse(
            error=error, details=exc.errors()
        ).model_dump(exclude_none=True),
    )


async def service_exception_handler(request: Request, exc: BaseServiceException) -> JSONResponse:
    """
    서비스 레이어 예외를 API 응답으로 변환하는 핸들러
    """
    if isinstance(exc, ValidationError):
        error_code = ErrorCode.INVALID_PARAM
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, (DatabaseError, SearchError, LLMError)):
        error_code = ErrorCode.SERVER_ERROR
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        error_code = ErrorCode.SERVER_ERROR
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    error = Error(code=error_code, message=exc.message)
    
    logger.error(
        f"Service Exception: {type(exc).__name__} - {exc.message}",
        extra={
            "details": exc.details,
            "original_exception": str(exc.original_exception) if exc.original_exception else None
        }
    )
    
    return JSONResponse(
        status_code=status_code,
        content=BaseErrorResponse(error=error, details=exc.details).model_dump(exclude_none=True),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    처리되지 않은 모든 예외 핸들러
    500/SERVER_ERROR로 변환하고 스택 트레이스 로깅
    """
    error = Error(code=ErrorCode.SERVER_ERROR, message="서버에 예기치 않은 오류가 발생했습니다.")
    logger.error("Unhandled Exception", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=BaseErrorResponse(error=error).model_dump(exclude_none=True),
    )

async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    FastAPI/Starlette 기본 HTTP 예외(예: 404)를 공통 에러 포맷으로 변환
    """
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code, message = ErrorCode.NOT_FOUND, "요청한 리소스를 찾을 수 없습니다."
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        code, message = ErrorCode.INVALID_PARAM, "요청 파라미터가 잘못되었습니다."
    else:
        code, message = ErrorCode.SERVER_ERROR, "오류가 발생했습니다."

    # detail이 문자열이면 메시지로 사용
    if isinstance(exc.detail, str) and exc.detail:
        message = exc.detail

    logger.warning(f"HTTPException: {exc.status_code} {message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseErrorResponse(error=Error(code=code, message=message)).model_dump(exclude_none=True),
    )