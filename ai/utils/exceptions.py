"""
공통 예외 처리 유틸리티
"""
from typing import Optional, Dict, Any
import traceback
from functools import wraps

from utils.logger import get_logger


class BaseServiceException(Exception):
    """서비스 레이어 기본 예외 클래스"""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        self.message = message
        self.details = details or {}
        self.original_exception = original_exception
        super().__init__(self.message)


class ConfigurationError(BaseServiceException):
    """설정 관련 오류"""
    pass


class DatabaseError(BaseServiceException):
    """데이터베이스 관련 오류"""
    pass


class LLMError(BaseServiceException):
    """LLM 관련 오류"""
    pass


class SearchError(BaseServiceException):
    """검색 관련 오류"""
    pass


class ValidationError(BaseServiceException):
    """유효성 검사 오류"""
    pass


def handle_service_exceptions(
    default_message: str = "서비스 처리 중 오류가 발생했습니다.",
    logger_name: Optional[str] = None
):
    """
    서비스 메서드의 예외를 처리하는 데코레이터
    
    Args:
        default_message: 기본 오류 메시지
        logger_name: 로거 이름 (None이면 함수의 모듈명 사용)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            try:
                return await func(*args, **kwargs)
            except BaseServiceException:
                # 이미 처리된 서비스 예외는 재발생
                raise
            except Exception as e:
                logger.error(
                    f"Unexpected error in {func.__name__}: {e}",
                    extra={
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs),
                        "traceback": traceback.format_exc()
                    }
                )
                raise BaseServiceException(
                    message=default_message,
                    details={"function": func.__name__, "original_error": str(e)},
                    original_exception=e
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            try:
                return func(*args, **kwargs)
            except BaseServiceException:
                # 이미 처리된 서비스 예외는 재발생
                raise
            except Exception as e:
                logger.error(
                    f"Unexpected error in {func.__name__}: {e}",
                    extra={
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs),
                        "traceback": traceback.format_exc()
                    }
                )
                raise BaseServiceException(
                    message=default_message,
                    details={"function": func.__name__, "original_error": str(e)},
                    original_exception=e
                )
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_and_reraise(
    logger_name: Optional[str] = None,
    log_level: str = "error"
):
    """
    예외를 로깅하고 재발생시키는 데코레이터
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log_method = getattr(logger, log_level.lower())
                log_method(
                    f"Exception in {func.__name__}: {e}",
                    extra={
                        "function": func.__name__,
                        "exception_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_method = getattr(logger, log_level.lower())
                log_method(
                    f"Exception in {func.__name__}: {e}",
                    extra={
                        "function": func.__name__,
                        "exception_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator