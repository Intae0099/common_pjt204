# 큐 시스템 가이드

> 리소스 제약 환경에서 안정적으로 동작하는 경량 큐 시스템 가이드

## 📋 목차

1. [개요](#개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [설치 및 설정](#설치-및-설정)
4. [사용법](#사용법)
5. [모니터링](#모니터링)
6. [설정 튜닝](#설정-튜닝)
7. [문제해결](#문제해결)

## 개요

ALaw AI 백엔드의 큐 시스템은 메모리/CPU 성능이 제한적인 환경에서도 안정적으로 동작하도록 설계된 SQLite 기반 경량 큐 시스템입니다.

### 주요 특징

- **보수적 리소스 관리**: 메모리 75%, CPU 80% 임계점 기반 처리 제어
- **서비스별 동시 처리 제한**: Case Analysis(1개), Search(2개), Chat(3개)
- **우선순위 기반 스케줄링**: 서비스 중요도에 따른 처리 순서 결정
- **장애 복구**: 타임아웃, 재시도, graceful degradation 지원

### 보수적 제한값

```python
CONSERVATIVE_LIMITS = {
    "case_analysis": {
        "max_concurrent": 1,        # 동시 처리 1개
        "max_queue_size": 5,        # 큐 크기 5개
        "timeout": 180,             # 3분 타임아웃
        "priority": 1               # 최고 우선순위
    },
    "search": {
        "max_concurrent": 2,        # 동시 처리 2개
        "max_queue_size": 10,       # 큐 크기 10개
        "timeout": 60,              # 1분 타임아웃
        "priority": 2
    },
    "consultation": {
        "max_concurrent": 1,        # 동시 처리 1개
        "max_queue_size": 5,        # 큐 크기 5개
        "timeout": 120,             # 2분 타임아웃
        "priority": 3
    },
    "structuring": {
        "max_concurrent": 2,        # 동시 처리 2개
        "max_queue_size": 8,        # 큐 크기 8개
        "timeout": 90,              # 1.5분 타임아웃
        "priority": 4
    },
    "chat": {
        "max_concurrent": 3,        # 동시 처리 3개
        "max_queue_size": 15,       # 큐 크기 15개
        "timeout": 30,              # 30초 타임아웃
        "priority": 5               # 최저 우선순위
    }
}
```

## 시스템 아키텍처

### 전체 아키텍처

```
User Request → API Router → Queue Manager → Resource Monitor → Service Execution
     ↓              ↓            ↓               ↓                    ↓
   HTTP req → FastAPI Route → SQLite Queue → CPU/Memory Check → Actual Service
     ↓              ↓            ↓               ↓                    ↓
 JSON resp ←   Response   ←  Result Wait  ←    Throttling     ←   Result Return
```

### 컴포넌트 구조

#### 1. LightweightQueueManager
- 큐 시스템의 중앙 관리자
- 워커 생명주기 관리
- 작업 제출 및 결과 대기

#### 2. SQLiteQueue
- SQLite 기반 영속성 큐
- 우선순위 기반 작업 스케줄링
- 큐 크기 제한 및 통계

#### 3. SimpleResourceMonitor
- 시스템 리소스 모니터링
- 캐시된 결과로 CPU 부하 최소화
- 임계점 기반 처리 제어

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install psutil>=5.9.0
```

### 2. 환경 변수 설정

```bash
# .env 파일에 추가 (선택사항)
QUEUE_DB_PATH=queue.db
MEMORY_THRESHOLD=75
CPU_THRESHOLD=80
```

### 3. FastAPI 앱 설정

큐 매니저는 FastAPI 앱 시작 시 자동으로 시작됩니다:

```python
# app/main.py에 이미 설정됨
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 큐 매니저 시작
    queue_manager = get_queue_manager()
    await queue_manager.start()
    
    yield
    
    # 큐 매니저 정지
    await queue_manager.stop()
```

## 사용법

### 1. 기본 사용법

```python
from services.lightweight_queue_manager import get_queue_manager

# 큐 매니저 가져오기
queue_manager = get_queue_manager()

# 작업 제출 및 결과 대기
result = await queue_manager.submit_and_wait(
    service_type="search",
    request_data={"query": "법률 검색"},
    user_id="user123",
    timeout=120
)
```

### 2. API를 통한 사용

#### Case Analysis API
```bash
POST /api/analysis
{
    "case": {
        "fullText": "사건 내용..."
    },
    "recommend_lawyers": true
}
```

#### Search API
```bash
GET /api/search/cases?keyword=계약분쟁&page=1&size=10
```

### 3. 큐 상태 확인

```bash
# 큐 상태 조회
curl http://localhost:8000/api/queue/status

# 응답 예시
{
    "queue_stats": {
        "search": {"pending": 2, "processing": 1, "completed": 45, "failed": 0}
    },
    "processing_count": {"search": 1, "case_analysis": 0},
    "resource_usage": {
        "memory_percent": 45.2,
        "cpu_percent": 23.1,
        "memory_threshold": 75,
        "cpu_threshold": 80
    },
    "limits": {...},
    "is_running": true
}
```

## 모니터링

### 1. 헬스체크

```bash
curl http://localhost:8000/api/queue/health
```

### 2. 상세 모니터링

```python
# 프로그래매틱 모니터링
queue_manager = get_queue_manager()
status = await queue_manager.get_status()

print(f"Memory: {status['resource_usage']['memory_percent']}%")
print(f"CPU: {status['resource_usage']['cpu_percent']}%")
print(f"Queue sizes: {status['queue_stats']}")
```

### 3. 로그 모니터링

큐 시스템은 상세한 로그를 제공합니다:

```
[INFO] Task enqueued: search:123 (queue_size: 3)
[INFO] Processing task 123 (search)
[INFO] Task 123 completed successfully
[WARNING] Memory usage too high: 78%
```

## 설정 튜닝

### 1. 성능이 좋은 환경에서의 설정

```python
# services/lightweight_queue_manager.py 수정
OPTIMIZED_LIMITS = {
    "case_analysis": {
        "max_concurrent": 2,        # 1 → 2로 증가
        "max_queue_size": 10,       # 5 → 10으로 증가
        "timeout": 300
    },
    "search": {
        "max_concurrent": 4,        # 2 → 4로 증가
        "max_queue_size": 20,       # 10 → 20으로 증가
        "timeout": 90
    }
}
```

### 2. 더 보수적인 설정

```python
ULTRA_CONSERVATIVE_LIMITS = {
    "case_analysis": {
        "max_concurrent": 1,
        "max_queue_size": 3,        # 5 → 3으로 감소
        "timeout": 120              # 180 → 120으로 감소
    }
}
```

### 3. 리소스 임계점 조정

```python
class SimpleResourceMonitor:
    def __init__(self):
        self.memory_threshold = 70  # 75 → 70으로 더 보수적
        self.cpu_threshold = 75     # 80 → 75로 더 보수적
```

## 문제해결

### 1. 큐가 가득 참

**증상**: `QueueFullError` 발생

**해결방법**:
```python
# 큐 크기 증가
CONSERVATIVE_LIMITS["search"]["max_queue_size"] = 20

# 또는 처리 속도 증가
CONSERVATIVE_LIMITS["search"]["max_concurrent"] = 3
```

### 2. 리소스 부족

**증상**: `ResourceExhaustionError` 발생

**해결방법**:
```python
# 임계점 완화
monitor.memory_threshold = 85  # 75 → 85
monitor.cpu_threshold = 90     # 80 → 90

# 또는 처리량 감소
CONSERVATIVE_LIMITS["case_analysis"]["max_concurrent"] = 1
```

### 3. 타임아웃 발생

**증상**: `Task timeout` 로그

**해결방법**:
```python
# 타임아웃 증가
CONSERVATIVE_LIMITS["case_analysis"]["timeout"] = 300  # 180 → 300

# 또는 처리량 감소로 개별 작업 속도 향상
CONSERVATIVE_LIMITS["case_analysis"]["max_concurrent"] = 1
```

### 4. 큐 시스템이 시작되지 않음

**확인사항**:
1. `psutil` 패키지 설치 여부
2. SQLite 데이터베이스 파일 권한
3. FastAPI lifespan 설정

**디버깅**:
```python
# 수동 시작으로 디버깅
queue_manager = get_queue_manager()
try:
    await queue_manager.start()
    print("Queue started successfully")
except Exception as e:
    print(f"Queue start failed: {e}")
```

### 5. 성능 최적화

**SQLite 최적화**:
```python
# 데이터베이스 연결 최적화
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=10000")
```

**리소스 모니터링 최적화**:
```python
# 체크 간격 증가
self.check_interval = 10  # 5초 → 10초
```

## 테스트

### 단위 테스트 실행

```bash
pytest tests/test_queue_system.py -v
```

### 부하 테스트

```python
import asyncio
import aiohttp

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):
            task = session.get('http://localhost:8000/api/queue/status')
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        print(f"Completed {len(responses)} requests")

# 실행
asyncio.run(load_test())
```

## 백업 및 복구

### 큐 데이터베이스 백업

```bash
# SQLite 백업
cp queue.db queue_backup_$(date +%Y%m%d_%H%M%S).db
```

### 복구

```bash
# 백업에서 복구
cp queue_backup_20231201_143022.db queue.db
```

## 마이그레이션

### Redis로 마이그레이션 (향후)

SQLite에서 Redis로 마이그레이션하려면:

1. Redis 서버 설정
2. `RedisQueue` 클래스 구현
3. 기존 SQLite 데이터 마이그레이션
4. 설정 변경

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLite 공식 문서](https://sqlite.org/docs.html)
- [psutil 공식 문서](https://psutil.readthedocs.io/)
- [프로젝트 아키텍처 문서](docs/ARCHITECTURE.md)