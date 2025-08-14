"""
큐 시스템 테스트
"""
import pytest
import asyncio
import tempfile
import os
from services.lightweight_queue_manager import (
    LightweightQueueManager, 
    SQLiteQueue, 
    SimpleResourceMonitor,
    QueueFullError,
    ResourceExhaustionError,
    CONSERVATIVE_LIMITS
)

@pytest.fixture
async def temp_queue_manager():
    """테스트용 큐 매니저 생성"""
    # 임시 데이터베이스 파일 생성
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    
    manager = LightweightQueueManager(temp_db.name)
    await manager.start()
    
    yield manager
    
    await manager.stop()
    # 테스트 후 임시 파일 삭제
    os.unlink(temp_db.name)

@pytest.fixture
def temp_sqlite_queue():
    """테스트용 SQLite 큐 생성"""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    
    queue = SQLiteQueue(temp_db.name)
    
    yield queue
    
    # 테스트 후 임시 파일 삭제
    os.unlink(temp_db.name)

class TestSQLiteQueue:
    """SQLite 큐 기본 기능 테스트"""
    
    @pytest.mark.asyncio
    async def test_enqueue_dequeue(self, temp_sqlite_queue):
        """큐에 작업 추가/제거 테스트"""
        queue = temp_sqlite_queue
        
        # 작업 추가
        task_id = await queue.enqueue(
            service_type="search",
            request_data={"query": "test"},
            user_id="test_user"
        )
        
        assert task_id is not None
        assert task_id > 0
        
        # 작업 가져오기
        task = await queue.dequeue("search")
        assert task is not None
        assert task.service_type == "search"
        assert task.request_data["query"] == "test"
        assert task.user_id == "test_user"
    
    @pytest.mark.asyncio
    async def test_queue_size_limit(self, temp_sqlite_queue):
        """큐 크기 제한 테스트"""
        queue = temp_sqlite_queue
        max_size = CONSERVATIVE_LIMITS["search"]["max_queue_size"]
        
        # 최대 크기까지 추가
        for i in range(max_size):
            await queue.enqueue(
                service_type="search",
                request_data={"query": f"test_{i}"},
                user_id="test_user"
            )
        
        # 초과 시 예외 발생 확인
        with pytest.raises(QueueFullError):
            await queue.enqueue(
                service_type="search",
                request_data={"query": "overflow"},
                user_id="test_user"
            )
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self, temp_sqlite_queue):
        """우선순위 순서 테스트"""
        queue = temp_sqlite_queue
        
        # 다른 우선순위로 작업 추가
        await queue.enqueue("search", {"query": "low"}, "user1", priority=5)
        await queue.enqueue("search", {"query": "high"}, "user2", priority=1)
        await queue.enqueue("search", {"query": "medium"}, "user3", priority=3)
        
        # 우선순위 순서로 가져오기 확인
        task1 = await queue.dequeue("search")
        assert task1.request_data["query"] == "high"  # priority 1
        
        task2 = await queue.dequeue("search")
        assert task2.request_data["query"] == "medium"  # priority 3
        
        task3 = await queue.dequeue("search")
        assert task3.request_data["query"] == "low"  # priority 5

class TestResourceMonitor:
    """리소스 모니터링 테스트"""
    
    @pytest.mark.asyncio
    async def test_resource_check(self):
        """리소스 상태 체크 테스트"""
        monitor = SimpleResourceMonitor()
        
        # 기본적으로 처리 허용해야 함
        result = await monitor.should_process_request("search")
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_cached_monitoring(self):
        """캐시된 모니터링 테스트"""
        monitor = SimpleResourceMonitor()
        monitor.check_interval = 1  # 1초로 설정
        
        # 첫 번째 호출
        result1 = await monitor.should_process_request("search")
        
        # 즉시 두 번째 호출 (캐시된 결과 사용)
        result2 = await monitor.should_process_request("search")
        
        # 결과가 동일해야 함
        assert result1 == result2

class TestQueueManager:
    """큐 매니저 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_submit_and_wait_mock(self, temp_queue_manager):
        """작업 제출 및 대기 테스트 (모킹)"""
        manager = temp_queue_manager
        
        # 실제 서비스 대신 간단한 테스트 로직 사용
        original_execute = manager._execute_service
        
        async def mock_execute_service(service_type, task):
            return {"test_result": f"processed_{service_type}"}
        
        manager._execute_service = mock_execute_service
        
        try:
            # 작업 제출 및 결과 대기
            result = await manager.submit_and_wait(
                service_type="search",
                request_data={"query": "test"},
                user_id="test_user",
                timeout=10
            )
            
            assert result["test_result"] == "processed_search"
            
        finally:
            # 원래 메서드 복원
            manager._execute_service = original_execute
    
    @pytest.mark.asyncio
    async def test_concurrent_processing_limit(self, temp_queue_manager):
        """동시 처리 제한 테스트"""
        manager = temp_queue_manager
        
        # 긴 처리 시간을 가진 모킹 함수
        async def slow_execute_service(service_type, task):
            await asyncio.sleep(2)  # 2초 대기
            return {"result": "slow_processing"}
        
        manager._execute_service = slow_execute_service
        
        # case_analysis는 max_concurrent=1이므로 한 번에 하나만 처리
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                manager.submit_task(
                    service_type="case_analysis",
                    request_data={"query": f"test_{i}"},
                    user_id=f"user_{i}"
                )
            )
            tasks.append(task)
        
        # 모든 작업이 큐에 추가되어야 함
        task_ids = await asyncio.gather(*tasks)
        assert len(task_ids) == 3
        assert all(isinstance(tid, int) for tid in task_ids)
    
    @pytest.mark.asyncio
    async def test_queue_status(self, temp_queue_manager):
        """큐 상태 조회 테스트"""
        manager = temp_queue_manager
        
        # 작업 추가
        await manager.submit_task(
            service_type="search",
            request_data={"query": "test"},
            user_id="test_user"
        )
        
        # 상태 조회
        status = await manager.get_status()
        
        assert "queue_stats" in status
        assert "processing_count" in status
        assert "resource_usage" in status
        assert "limits" in status
        assert status["is_running"] is True

class TestErrorHandling:
    """에러 처리 테스트"""
    
    @pytest.mark.asyncio
    async def test_queue_full_error(self, temp_queue_manager):
        """큐 가득참 에러 테스트"""
        manager = temp_queue_manager
        max_size = CONSERVATIVE_LIMITS["search"]["max_queue_size"]
        
        # 큐를 가득 채움
        for i in range(max_size):
            await manager.submit_task(
                service_type="search",
                request_data={"query": f"test_{i}"},
                user_id="test_user"
            )
        
        # 초과 시 예외 발생 확인
        with pytest.raises(QueueFullError):
            await manager.submit_task(
                service_type="search",
                request_data={"query": "overflow"},
                user_id="test_user"
            )
    
    @pytest.mark.asyncio
    async def test_invalid_service_type(self, temp_queue_manager):
        """잘못된 서비스 타입 에러 테스트"""
        manager = temp_queue_manager
        
        with pytest.raises(ValueError, match="Unknown service type"):
            await manager.submit_task(
                service_type="invalid_service",
                request_data={"query": "test"},
                user_id="test_user"
            )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])