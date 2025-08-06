
import logging
import logging.config
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any

from config.settings import get_logging_settings


class CustomFormatter(logging.Formatter):
    """시간 포맷을 원하는 형식으로 변경하는 커스텀 포매터"""
    
    def formatTime(self, record, datefmt=None):
        if datefmt:
            return datetime.fromtimestamp(record.created).strftime(datefmt)
        return datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')


def setup_logger():
    """전역 로깅 설정을 초기화합니다."""
    logging_settings = get_logging_settings()
    
    LOG_DIR = "logs"
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    log_file = f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # 커스텀 포매터 생성
    formatter = CustomFormatter(
        fmt=logging_settings.format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handlers = []
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # 파일 로깅이 설정된 경우 파일 핸들러 추가
    if logging_settings.file_path or True:  # 기본적으로 파일 로깅 사용
        file_path = logging_settings.file_path or os.path.join(LOG_DIR, log_file)
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, logging_settings.level.upper()))
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 새 핸들러 추가
    for handler in handlers:
        root_logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스를 반환합니다."""
    return logging.getLogger(name)


class LoggerMixin:
    """
    클래스에 로거 기능을 추가하는 Mixin 클래스
    """
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
    
    def log_info_with_duration(self, message: str, duration_ms: Optional[float] = None):
        """실행 시간을 포함한 정보 로그"""
        log_with_duration(self.logger, message, duration_ms)
    
    def log_start(self, operation: str):
        """작업 시작 로그"""
        self.logger.info(f"{operation} 시작")
        return time.time()
    
    def log_complete(self, operation: str, start_time: float):
        """작업 완료 로그 (시작 시간으로부터 계산)"""
        duration_ms = (time.time() - start_time) * 1000
        self.log_info_with_duration(f"{operation} 완료", duration_ms)


def log_with_duration(logger: logging.Logger, message: str, duration_ms: Optional[float] = None):
    """실행 시간을 포함한 로그 메시지를 출력합니다."""
    if duration_ms is not None:
        formatted_message = f"{message} [{duration_ms:.0f}ms]"
    else:
        formatted_message = message
    logger.info(formatted_message)


def log_execution_time(func):
    """
    함수 실행 시간을 로깅하는 데코레이터
    """
    import functools
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            log_with_duration(logger, f"{func.__name__} 처리 완료", duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} 실행 실패 [{duration_ms:.0f}ms]: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            log_with_duration(logger, f"{func.__name__} 처리 완료", duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} 실행 실패 [{duration_ms:.0f}ms]: {e}")
            raise
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
