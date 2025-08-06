"""
API 라우터 공통 데코레이터
"""
from functools import wraps
from typing import Callable, Any, Optional, Type
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.api.response_models import success_response, error_response
from utils.exceptions import BaseServiceException
from utils.logger import get_logger

logger = get_logger(__name__)


def handle_api_exceptions(
    success_message: Optional[str] = None,
    error_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
):
    """
    API 엔드포인트의 예외를 처리하는 데코레이터
    
    Args:
        success_message: 성공 시 반환할 메시지
        error_status_code: 기본 에러 상태 코드
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # 결과가 이미 Response 객체인 경우 그대로 반환
                if isinstance(result, JSONResponse):
                    return result
                elif isinstance(result, dict):
                    if 'success' in result:
                        # 이미 성공 응답 형태인 경우 그대로 반환
                        return result
                    else:
                        # 일반 dict인 경우 성공 응답으로 래핑
                        return success_response(data=result, message=success_message)
                
                # 기타 결과는 성공 응답으로 래핑
                return success_response(data=result, message=success_message)
                
            except BaseServiceException as e:
                logger.warning(f"Service exception in {func.__name__}: {e.message}")
                error_resp = error_response(
                    message=e.message,
                    error_details=e.details
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=error_resp.model_dump()
                )
            except HTTPException:
                # FastAPI HTTPException은 그대로 재발생
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                error_resp = error_response(
                    message="서버 내부 오류가 발생했습니다.",
                    error_details={"detail": str(e)}
                )
                return JSONResponse(
                    status_code=error_status_code,
                    content=error_resp.model_dump()
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # 결과가 이미 Response 객체인 경우 그대로 반환
                if isinstance(result, JSONResponse):
                    return result
                elif isinstance(result, dict):
                    if 'success' in result:
                        # 이미 성공 응답 형태인 경우 그대로 반환
                        return result
                    else:
                        # 일반 dict인 경우 성공 응답으로 래핑
                        return success_response(data=result, message=success_message)
                
                # 기타 결과는 성공 응답으로 래핑
                return success_response(data=result, message=success_message)
                
            except BaseServiceException as e:
                logger.warning(f"Service exception in {func.__name__}: {e.message}")
                error_resp = error_response(
                    message=e.message,
                    error_details=e.details
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=error_resp.model_dump()
                )
            except HTTPException:
                # FastAPI HTTPException은 그대로 재발생
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                error_resp = error_response(
                    message="서버 내부 오류가 발생했습니다.",
                    error_details={"detail": str(e)}
                )
                return JSONResponse(
                    status_code=error_status_code,
                    content=error_resp.model_dump()
                )
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_pagination(max_size: int = 50):
    """
    페이지네이션 파라미터를 검증하는 데코레이터
    
    Args:
        max_size: 최대 페이지 크기
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 페이지네이션 파라미터 검증
            page = kwargs.get('page', 1)
            size = kwargs.get('size', 10)
            
            if page < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="페이지 번호는 1 이상이어야 합니다."
                )
            
            if size < 1 or size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"페이지 크기는 1 이상 {max_size} 이하여야 합니다."
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 페이지네이션 파라미터 검증
            page = kwargs.get('page', 1)
            size = kwargs.get('size', 10)
            
            if page < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="페이지 번호는 1 이상이어야 합니다."
                )
            
            if size < 1 or size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"페이지 크기는 1 이상 {max_size} 이하여야 합니다."
                )
            
            return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator