# app/api/routers/queue_status.py
"""
큐 상태 모니터링 API
"""
from fastapi import APIRouter, status
from services.lightweight_queue_manager import get_queue_manager

router = APIRouter()

@router.get(
    "/queue/status",
    status_code=status.HTTP_200_OK,
    tags=["Queue"],
    summary="큐 상태 조회",
    description="현재 큐 상태와 리소스 사용량을 조회합니다.",
)
async def get_queue_status():
    """
    큐 상태 조회 API
    - 각 서비스별 큐 통계
    - 현재 처리 중인 작업 수
    - 시스템 리소스 사용량
    """
    queue_manager = get_queue_manager()
    return await queue_manager.get_status()

@router.get(
    "/queue/health",
    status_code=status.HTTP_200_OK,
    tags=["Queue"],
    summary="큐 시스템 헬스체크",
    description="큐 시스템의 동작 상태를 확인합니다.",
)
async def queue_health_check():
    """큐 시스템 헬스체크"""
    queue_manager = get_queue_manager()
    
    try:
        status_info = await queue_manager.get_status()
        is_healthy = status_info["is_running"]
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "is_running": is_healthy,
            "message": "Queue system is operational" if is_healthy else "Queue system is not running"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "is_running": False,
            "message": f"Queue system error: {str(e)}"
        }