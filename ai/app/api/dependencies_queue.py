"""
큐 시스템을 위한 의존성 함수들
"""
from services.lightweight_queue_manager import get_queue_manager, LightweightQueueManager

def get_queue_service() -> LightweightQueueManager:
    """큐 매니저 의존성 주입"""
    return get_queue_manager()