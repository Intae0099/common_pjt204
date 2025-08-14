"""
리소스 제약 환경을 위한 경량화 큐 관리자

메모리와 CPU가 제한적인 환경에서 안정적으로 동작하는 보수적인 큐 시스템
- SQLite 기반 영속성 큐 (Redis 대신)
- 매우 보수적인 동시 처리 제한
- 간단한 리소스 모니터링
- 메모리 누수 방지
"""

import asyncio
import sqlite3
import json
import psutil
import gc
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
from utils.logger import get_logger

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime, date and Pydantic objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        # Handle Pydantic models
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        # Handle dataclasses
        if hasattr(obj, '__dataclass_fields__'):
            return {field.name: getattr(obj, field.name) for field in obj.__dataclass_fields__.values()}
        return super().default(obj)

logger = get_logger(__name__)

@dataclass
class QueueTask:
    id: int
    service_type: str
    priority: int
    request_data: Dict[str, Any]
    user_id: str
    created_at: datetime
    status: str
    retry_count: int

class QueueFullError(Exception):
    """큐가 가득 찬 경우 발생하는 예외"""
    pass

class ResourceExhaustionError(Exception):
    """리소스 부족으로 처리할 수 없는 경우 발생하는 예외"""
    pass

# 매우 보수적인 리소스 제한 설정
CONSERVATIVE_LIMITS = {
    "case_analysis": {
        "max_concurrent": 1,        # 가장 리소스 집약적
        "max_queue_size": 5,        # 큐 크기도 작게
        "timeout": 180,             # 3분 타임아웃
        "priority": 1               # 높은 우선순위
    },
    "search": {
        "max_concurrent": 2,        # 검색은 상대적으로 가벼움
        "max_queue_size": 10,
        "timeout": 60,              # 1분 타임아웃
        "priority": 2
    },
    "consultation": {
        "max_concurrent": 1,        # LLM 다중 호출로 리소스 집약적
        "max_queue_size": 5,
        "timeout": 120,             # 2분 타임아웃
        "priority": 3
    },
    "structuring": {
        "max_concurrent": 2,        # 비교적 가벼움
        "max_queue_size": 8,
        "timeout": 90,
        "priority": 4
    },
    "chat": {
        "max_concurrent": 3,        # 스트리밍, 상대적으로 가벼움
        "max_queue_size": 15,
        "timeout": 30,
        "priority": 5               # 낮은 우선순위
    }
}

class SimpleResourceMonitor:
    """간단한 리소스 모니터링 (CPU 부하 최소화)"""
    
    def __init__(self):
        self.memory_threshold = 95    # 95% 메모리 사용 시 제한 (완화)
        self.cpu_threshold = 95       # 95% CPU 사용 시 제한 (완화)
        self.last_check = 0
        self.check_interval = 5       # 5초마다만 체크
        self.cached_status = True
    
    async def should_process_request(self, service_type: str = None) -> bool:
        """리소스 상태 체크 (캐시된 결과 사용으로 부하 최소화)"""
        import time
        current_time = time.time()
        
        # 캐시된 결과 사용 (5초 이내)
        if current_time - self.last_check < self.check_interval:
            return self.cached_status
        
        try:
            # 간단한 리소스 체크
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=0.1)  # 매우 짧은 간격
            
            # 완화된 기준 적용 (95%)
            if memory_percent > self.memory_threshold:
                logger.warning(f"Memory usage too high: {memory_percent}%")
                self.cached_status = False
            elif cpu_percent > self.cpu_threshold:
                logger.warning(f"CPU usage too high: {cpu_percent}%")
                self.cached_status = False
            else:
                self.cached_status = True
                
            self.last_check = current_time
            return self.cached_status
            
        except Exception as e:
            logger.error(f"Resource monitoring failed: {e}")
            return True  # 모니터링 실패 시 기본 허용

class SQLiteQueue:
    """SQLite 기반 경량 큐 (메모리 절약)"""
    
    def __init__(self, db_path: str = "db/queue.db"):
        self.db_path = db_path
        self.lock = asyncio.Lock()
        self._init_db()
    
    def _init_db(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_type TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                request_data TEXT NOT NULL,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                completed_at TIMESTAMP,
                result TEXT
            )
        """)
        
        # Add result column if it doesn't exist (for existing databases)
        try:
            conn.execute("ALTER TABLE queue ADD COLUMN result TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # 인덱스 생성 (성능 최적화)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_service_status_priority ON queue(service_type, status, priority)")
        conn.commit()
        conn.close()
    
    async def enqueue(self, service_type: str, request_data: Dict[str, Any], 
                     user_id: str, priority: Optional[int] = None) -> int:
        """큐에 작업 추가"""
        async with self.lock:
            # 큐 크기 체크 (메모리 보호)
            queue_size = await self._get_queue_size(service_type)
            max_size = CONSERVATIVE_LIMITS[service_type]["max_queue_size"]
            
            if queue_size >= max_size:
                raise QueueFullError(f"{service_type} 큐가 가득 찼습니다 ({queue_size}/{max_size})")
            
            # 우선순위 설정
            if priority is None:
                priority = CONSERVATIVE_LIMITS[service_type]["priority"]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                INSERT INTO queue (service_type, priority, request_data, user_id)
                VALUES (?, ?, ?, ?)
            """, (service_type, priority, json.dumps(request_data), user_id))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Task enqueued: {service_type}:{task_id} (queue_size: {queue_size + 1})")
            return task_id
    
    async def dequeue(self, service_type: str) -> Optional[QueueTask]:
        """우선순위 기반으로 작업 가져오기"""
        async with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT id, service_type, priority, request_data, user_id, created_at, status, retry_count
                FROM queue 
                WHERE service_type = ? AND status = 'pending'
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
            """, (service_type,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            
            # 작업 상태를 'processing'으로 변경
            task_id = row[0]
            conn.execute("UPDATE queue SET status = 'processing' WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            
            return QueueTask(
                id=task_id,
                service_type=row[1],
                priority=row[2],
                request_data=json.loads(row[3]),
                user_id=row[4],
                created_at=datetime.fromisoformat(row[5]),
                status='processing',
                retry_count=row[7]
            )
    
    async def mark_completed(self, task_id: int, result: Any = None):
        """작업 완료 처리"""
        conn = sqlite3.connect(self.db_path)
        result_json = json.dumps(result, cls=DateTimeEncoder) if result is not None else None
        conn.execute("""
            UPDATE queue 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP, result = ?
            WHERE id = ?
        """, (result_json, task_id))
        conn.commit()
        conn.close()
        logger.info(f"Task completed: {task_id}")
    
    async def mark_failed(self, task_id: int, error_message: str):
        """작업 실패 처리"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE queue 
            SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (error_message, task_id))
        conn.commit()
        conn.close()
        logger.error(f"Task failed: {task_id} - {error_message}")
    
    async def _get_queue_size(self, service_type: str) -> int:
        """큐 크기 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT COUNT(*) FROM queue 
            WHERE service_type = ? AND status IN ('pending', 'processing')
        """, (service_type,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    async def get_queue_stats(self) -> Dict[str, Dict[str, int]]:
        """큐 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT service_type, status, COUNT(*) 
            FROM queue 
            GROUP BY service_type, status
        """)
        
        stats = {}
        for service_type, status, count in cursor.fetchall():
            if service_type not in stats:
                stats[service_type] = {'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}
            stats[service_type][status] = count
        
        conn.close()
        return stats

class LightweightQueueManager:
    """경량화 큐 관리자"""
    
    def __init__(self, db_path: str = "db/queue.db"):
        self.queue = SQLiteQueue(db_path)
        self.monitor = SimpleResourceMonitor()
        self.workers = {}  # service_type별 워커
        self.processing_count = {}  # service_type별 현재 처리 중인 작업 수
        self.is_running = False
    
    async def start(self):
        """큐 매니저 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting lightweight queue manager...")
        
        # 각 서비스 타입별로 워커 시작
        for service_type in CONSERVATIVE_LIMITS.keys():
            self.processing_count[service_type] = 0
            # 각 서비스별로 단일 워커만 생성 (리소스 절약)
            self.workers[service_type] = asyncio.create_task(
                self._worker_loop(service_type)
            )
        
        logger.info("Queue manager started with conservative settings")
    
    async def stop(self):
        """큐 매니저 중지"""
        self.is_running = False
        logger.info("Stopping queue manager...")
        
        # 모든 워커 종료
        for worker in self.workers.values():
            worker.cancel()
        
        await asyncio.gather(*self.workers.values(), return_exceptions=True)
        logger.info("Queue manager stopped")
    
    async def submit_task(self, service_type: str, request_data: Dict[str, Any], 
                         user_id: str, priority: Optional[int] = None) -> int:
        """작업 제출"""
        if not self.is_running:
            raise RuntimeError("Queue manager is not running")
        
        if service_type not in CONSERVATIVE_LIMITS:
            raise ValueError(f"Unknown service type: {service_type}")
        
        # 리소스 상태 체크
        if not await self.monitor.should_process_request(service_type):
            raise ResourceExhaustionError("시스템 리소스가 부족합니다. 잠시 후 다시 시도해주세요.")
        
        return await self.queue.enqueue(service_type, request_data, user_id, priority)
    
    async def _worker_loop(self, service_type: str):
        """워커 루프 (서비스별 단일 워커)"""
        logger.info(f"Starting worker for {service_type}")
        
        while self.is_running:
            try:
                # 리소스 상태 체크
                if not await self.monitor.should_process_request(service_type):
                    await asyncio.sleep(10)  # 리소스 부족 시 대기
                    continue
                
                # 동시 처리 제한 체크
                current_processing = self.processing_count[service_type]
                max_concurrent = CONSERVATIVE_LIMITS[service_type]["max_concurrent"]
                
                if current_processing >= max_concurrent:
                    await asyncio.sleep(2)  # 제한 도달 시 대기
                    continue
                
                # 작업 가져오기
                task = await self.queue.dequeue(service_type)
                if not task:
                    await asyncio.sleep(1)  # 작업 없으면 짧은 대기
                    continue
                
                # 작업 처리
                await self._process_task(service_type, task)
                
            except Exception as e:
                logger.error(f"Worker error for {service_type}: {e}")
                await asyncio.sleep(5)  # 에러 시 대기
        
        logger.info(f"Worker stopped for {service_type}")
    
    async def _process_task(self, service_type: str, task: QueueTask):
        """안전한 작업 처리"""
        self.processing_count[service_type] += 1
        
        try:
            logger.info(f"Processing task {task.id} ({service_type})")
            
            # 타임아웃 설정
            timeout = CONSERVATIVE_LIMITS[service_type]["timeout"]
            
            # 실제 서비스 호출 (타임아웃 적용)
            result = await asyncio.wait_for(
                self._execute_service(service_type, task),
                timeout=timeout
            )
            
            await self.queue.mark_completed(task.id, result)
            logger.info(f"Task {task.id} completed successfully")
            
        except asyncio.TimeoutError:
            error_msg = f"Task timeout after {timeout}s"
            logger.warning(f"Task {task.id} timed out")
            await self.queue.mark_failed(task.id, error_msg)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Task {task.id} failed: {error_msg}")
            await self.queue.mark_failed(task.id, error_msg)
            
        finally:
            self.processing_count[service_type] -= 1
            # 명시적 가비지 컬렉션 (메모리 절약)
            gc.collect()
    
    async def _execute_service(self, service_type: str, task: QueueTask) -> Any:
        """실제 서비스 호출"""
        logger.info(f"Executing {service_type} service with data: {task.request_data}")
        
        try:
            if service_type == "case_analysis":
                return await self._execute_case_analysis(task)
            elif service_type == "search":
                return await self._execute_search(task)
            elif service_type == "consultation":
                return await self._execute_consultation(task)
            elif service_type == "structuring":
                return await self._execute_structuring(task)
            elif service_type == "chat":
                return await self._execute_chat(task)
            else:
                raise ValueError(f"Unknown service type: {service_type}")
                
        except Exception as e:
            logger.error(f"Service execution failed for {service_type}: {e}")
            raise
    
    async def _execute_case_analysis(self, task: QueueTask) -> Any:
        """Case Analysis Service 실행"""
        from app.api.dependencies import get_case_analysis_service
        from core.container import get_container
        
        # 의존성 주입 컨테이너에서 서비스 가져오기
        container = get_container()
        service = container.case_analysis_service()
        
        request_data = task.request_data
        result = await service.analyze_case(
            user_query=request_data["user_query"],
            top_k_docs=request_data.get("top_k_docs", 15),
            recommend_lawyers=request_data.get("recommend_lawyers", True)
        )
        return result
    
    async def _execute_search(self, task: QueueTask) -> Any:
        """Search Service 실행"""
        from core.container import get_container
        
        container = get_container()
        service = container.search_service()
        
        request_data = task.request_data
        result = await service.vector_search(
            query=request_data["query"],
            page=request_data.get("page", 1),
            size=request_data.get("size", 10),
            use_rerank=request_data.get("use_rerank", True)
        )
        return {"search_results": result[0], "total_count": result[1]}
    
    async def _execute_consultation(self, task: QueueTask) -> Any:
        """Consultation Service 실행"""
        from core.container import get_container
        from app.api.schemas.consult import ConsultationRequest, CaseInfo
        
        container = get_container()
        service = container.consultation_service()
        
        request_data = task.request_data
        
        # ConsultationRequest 객체 생성
        case_info = CaseInfo(**request_data["case"])
        consultation_request = ConsultationRequest(
            case=case_info,
            weakPoints=request_data.get("weakPoints", ""),
            desiredOutcome=request_data.get("desiredOutcome", "")
        )
        
        result = await service.create_application_and_questions(consultation_request)
        return result
    
    async def _execute_structuring(self, task: QueueTask) -> Any:
        """Structuring Service 실행"""
        from core.container import get_container
        
        container = get_container()
        service = container.structuring_service()
        
        request_data = task.request_data
        result = await service.structure_case(request_data["free_text"])
        return result
    
    async def _execute_chat(self, task: QueueTask) -> Any:
        """Chat Service 실행 (스트리밍은 별도 처리 필요)"""
        from core.container import get_container
        from app.api.schemas.chat import ChatRequest
        
        container = get_container()
        service = container.chat_service()
        
        request_data = task.request_data
        chat_request = ChatRequest(message=request_data["message"])
        
        # 스트리밍 대신 일괄 응답으로 변경
        response_chunks = []
        async for chunk in service.stream_chat_response(chat_request, task.user_id):
            if chunk.strip() and not chunk.endswith("[DONE]"):
                response_chunks.append(chunk)
        
        return {"response": "".join(response_chunks)}
    
    async def wait_for_result(self, task_id: int, timeout: int = 300) -> Any:
        """작업 결과 대기 (폴링 방식)"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # 타임아웃 체크
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise asyncio.TimeoutError(f"Task {task_id} timed out after {timeout}s")
            
            # 작업 상태 확인
            status = await self._get_task_status(task_id)
            
            if status["status"] == "completed":
                return status.get("result")
            elif status["status"] == "failed":
                raise Exception(f"Task {task_id} failed: {status.get('error_message', 'Unknown error')}")
            elif status["status"] in ["pending", "processing"]:
                await asyncio.sleep(1)  # 1초 대기 후 다시 확인
            else:
                raise Exception(f"Unknown task status: {status['status']}")
    
    async def _get_task_status(self, task_id: int) -> Dict[str, Any]:
        """작업 상태 조회"""
        conn = sqlite3.connect(self.queue.db_path)
        cursor = conn.execute("""
            SELECT status, error_message, completed_at, result 
            FROM queue 
            WHERE id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"status": "not_found"}
        
        result = None
        if row[3]:  # result column
            try:
                result = json.loads(row[3])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse result for task {task_id}")
                result = None
        
        return {
            "status": row[0],
            "error_message": row[1],
            "completed_at": row[2],
            "result": result
        }
    
    async def submit_and_wait(self, service_type: str, request_data: Dict[str, Any], 
                             user_id: str, priority: Optional[int] = None, 
                             timeout: int = 300) -> Any:
        """작업 제출 후 결과 대기 (편의 메서드)"""
        task_id = await self.submit_task(service_type, request_data, user_id, priority)
        return await self.wait_for_result(task_id, timeout)

    async def get_status(self) -> Dict[str, Any]:
        """큐 상태 조회"""
        stats = await self.queue.get_queue_stats()
        
        # 리소스 상태 추가
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 현재 시간 추가
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "queue_stats": stats,
            "processing_count": dict(self.processing_count),
            "resource_usage": {
                "memory_percent": memory_percent,
                "cpu_percent": cpu_percent,
                "memory_threshold": self.monitor.memory_threshold,
                "cpu_threshold": self.monitor.cpu_threshold
            },
            "limits": CONSERVATIVE_LIMITS,
            "is_running": self.is_running,
            "timestamp": current_time
        }

# 싱글톤 인스턴스
_queue_manager_instance = None

def get_queue_manager() -> LightweightQueueManager:
    """큐 매니저 싱글톤 인스턴스 반환"""
    global _queue_manager_instance
    if _queue_manager_instance is None:
        _queue_manager_instance = LightweightQueueManager()
    return _queue_manager_instance