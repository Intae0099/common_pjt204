# ⚙️ 개발 가이드

ALaw AI-Backend 개발을 위한 가이드입니다.

## 📋 목차

- [개발 환경 설정](#개발-환경-설정)
- [프로젝트 구조](#프로젝트-구조)
- [개발 워크플로우](#개발-워크플로우)
- [코딩 컨벤션](#코딩-컨벤션)
- [디버깅](#디버깅)
- [성능 최적화](#성능-최적화)

---

## 개발 환경 설정

### 1. 사전 요구사항

```bash
# Python 3.10+ 설치 확인
python --version

# Git 설치 확인
git --version

# Docker 설치 확인 (선택사항)
docker --version
```

### 2. 개발 환경 구성

```bash
# 리포지토리 클론
git clone https://github.com/your-repo/ALaw-AI-Backend.git
cd ALaw-AI-Backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 개발 의존성 설치
pip install -r requirements-dev.txt

# pre-commit 훅 설치
pre-commit install
```

### 3. 환경 변수 설정

```bash
# 개발용 환경 파일 생성
cp config/.env.example config/.env.dev

# 환경 변수 편집
nano config/.env.dev
```

**config/.env.dev 예시**:
```env
# 환경
ENVIRONMENT=development
DEBUG=true

# 데이터베이스
DATABASE_URL=postgresql://postgres:password@localhost:5432/alaw_ai_dev

# AI 모델
OPENAI_API_KEY=your-api-key-here
EMBEDDING_MODEL=snunlp/KR-SBERT-V40K-klueNLI-augSTS

# 로깅
LOG_LEVEL=DEBUG
LOG_FILE=logs/dev.log

# 큐 시스템
QUEUE_DB_PATH=data/queue_dev.db
```

### 4. 데이터베이스 설정

```bash
# PostgreSQL 개발 DB 생성
createdb alaw_ai_dev

# pgvector 확장 설치
psql alaw_ai_dev -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 스키마 초기화
psql alaw_ai_dev -f db/init_schema.sql
```

---

## 프로젝트 구조

```
ALaw-AI-Backend/
├── app/                    # FastAPI 애플리케이션
│   ├── api/               # API 라우터 및 엔드포인트
│   │   ├── routers/      # 각 기능별 라우터
│   │   ├── schemas/      # Pydantic 모델
│   │   └── handlers.py   # 예외 처리기
│   └── main.py           # 애플리케이션 진입점
├── services/              # 비즈니스 로직 서비스
│   ├── search_service.py     # 검색 관련
│   ├── case_analysis_service.py  # 케이스 분석
│   ├── chat_service.py       # 챗봇
│   └── ...
├── utils/                 # 유틸리티 함수
│   ├── logger.py         # 로깅 설정
│   ├── exceptions.py     # 커스텀 예외
│   └── confidence_calculator.py
├── config/                # 설정 파일
│   ├── settings.py       # 설정 클래스
│   └── .env.example     # 환경 변수 템플릿
├── db/                    # 데이터베이스 관련
│   ├── database.py       # DB 연결 설정
│   └── *.sql            # SQL 스크립트
├── llm/                   # LLM 관련 모듈
│   ├── models/          # 모델 래퍼
│   └── clients/         # LLM 클라이언트
├── tests/                 # 테스트 코드
│   ├── conftest.py      # 테스트 설정
│   ├── services/        # 서비스 테스트
│   └── api/             # API 테스트
├── docs/                  # 문서
├── docker/                # Docker 설정
└── requirements*.txt      # 의존성 목록
```

### 주요 모듈 설명

#### 1. Services Layer
```python
# services/base_service.py
class BaseService:
    """모든 서비스의 기본 클래스"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @handle_service_exceptions("서비스 처리 중 오류가 발생했습니다.")
    async def process(self, *args, **kwargs):
        # 공통 처리 로직
        pass
```

#### 2. API Layer
```python
# app/api/routers/example.py
from fastapi import APIRouter, Depends
from app.api.schemas.example import ExampleRequest, ExampleResponse

router = APIRouter(prefix="/api/example", tags=["example"])

@router.post("/", response_model=ExampleResponse)
async def process_example(
    request: ExampleRequest,
    service: ExampleService = Depends(get_example_service)
):
    result = await service.process(request)
    return ExampleResponse(data=result)
```

#### 3. Configuration
```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False
    database_url: str
    openai_api_key: str
    
    class Config:
        env_file = "config/.env"
```

---

## 개발 워크플로우

### 1. 기능 개발 프로세스

```bash
# 1. 새 브랜치 생성
git checkout -b feature/new-feature

# 2. 개발 진행
# - 코드 작성
# - 테스트 작성
# - 문서 업데이트

# 3. 테스트 실행
pytest tests/ -v

# 4. 코드 품질 검사
black .
isort .
flake8 .
mypy .

# 5. 커밋 및 푸시
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 6. Pull Request 생성
```

### 2. 테스트 주도 개발 (TDD)

```python
# 1. 실패하는 테스트 작성
def test_new_feature():
    service = NewService()
    result = service.new_method("input")
    assert result == "expected_output"

# 2. 최소한의 구현
class NewService:
    def new_method(self, input_data):
        return "expected_output"

# 3. 리팩토링
class NewService:
    def new_method(self, input_data):
        # 실제 로직 구현
        processed = self._process(input_data)
        return self._format_output(processed)
```

### 3. API 먼저 설계 (API-First)

```python
# 1. 스키마 정의
class AnalysisRequest(BaseModel):
    case_text: str = Field(..., min_length=10, max_length=10000)
    options: Dict[str, Any] = Field(default_factory=dict)

class AnalysisResponse(BaseModel):
    success: bool
    data: AnalysisResult
    confidence: float = Field(..., ge=0.0, le=1.0)

# 2. API 엔드포인트 정의
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_case(request: AnalysisRequest):
    # TODO: 구현
    pass

# 3. 서비스 로직 구현
class AnalysisService:
    async def analyze(self, case_text: str, options: dict) -> AnalysisResult:
        # 구현
        pass
```

---

## 코딩 컨벤션

### 1. Python 스타일 가이드

**Black + isort 설정** (pyproject.toml):
```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

### 2. 네이밍 컨벤션

```python
# 클래스: PascalCase
class SearchService:
    pass

# 함수/변수: snake_case
def analyze_case():
    user_input = "example"

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Private 멤버: 앞에 언더스코어
class Service:
    def __init__(self):
        self._private_var = None
    
    def _private_method(self):
        pass
```

### 3. 문서화

```python
class SearchService:
    """법률 판례 검색 서비스
    
    키워드 검색과 벡터 검색을 결합한 하이브리드 검색을 제공합니다.
    """
    
    async def vector_search(self, query: str, size: int = 10) -> tuple[list[dict], int]:
        """벡터 기반 유사성 검색
        
        Args:
            query: 검색 쿼리 문자열
            size: 반환할 결과 수 (기본값: 10)
            
        Returns:
            tuple: (검색 결과 리스트, 전체 결과 수)
            
        Raises:
            SearchError: 검색 처리 중 오류 발생 시
            ValidationError: 입력 데이터 검증 실패 시
            
        Example:
            >>> service = SearchService()
            >>> results, total = await service.vector_search("계약 위반", 5)
            >>> print(f"총 {total}개 중 {len(results)}개 결과")
        """
        pass
```

### 4. 에러 처리

```python
# 커스텀 예외 사용
from utils.exceptions import SearchError, ValidationError

class SearchService:
    @handle_service_exceptions("검색 처리 중 오류가 발생했습니다.")
    async def search(self, query: str) -> list[dict]:
        try:
            # 검색 로직
            results = await self._perform_search(query)
            return results
        except DatabaseError as e:
            # DB 오류는 SearchError로 변환
            raise SearchError(f"검색 중 데이터베이스 오류: {e}") from e
        except Exception as e:
            # 예상치 못한 오류는 데코레이터가 처리
            raise
```

---

## 디버깅

### 1. 로깅 설정

```python
# utils/logger.py 사용
from utils.logger import get_logger

logger = get_logger(__name__)

class SearchService:
    async def search(self, query: str):
        logger.info(f"검색 시작: query='{query}'")
        
        try:
            results = await self._search_impl(query)
            logger.info(f"검색 완료: {len(results)}개 결과")
            return results
        except Exception as e:
            logger.error(f"검색 실패: {e}", exc_info=True)
            raise
```

### 2. 디버깅 도구

```python
# 1. pdb 사용
import pdb; pdb.set_trace()

# 2. breakpoint() 사용 (Python 3.7+)
breakpoint()

# 3. 로그 기반 디버깅
logger.debug(f"변수 상태: {variable}")
logger.debug(f"함수 호출: {func.__name__}({args}, {kwargs})")
```

### 3. 테스트 디버깅

```bash
# 특정 테스트만 실행
pytest tests/test_search.py::test_vector_search -v

# 디버깅 모드로 실행
pytest --pdb tests/test_search.py

# 실패한 테스트만 재실행
pytest --lf

# 커버리지와 함께 실행
pytest --cov=services tests/
```

---

## 성능 최적화

### 1. 비동기 처리

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def parallel_processing(self, items: list):
        """여러 작업을 병렬로 처리"""
        tasks = [self._process_item(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]
    
    async def cpu_intensive_task(self, data):
        """CPU 집약적 작업을 별도 스레드에서 실행"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, 
            self._cpu_intensive_work, 
            data
        )
        return result
```

### 2. 메모리 최적화

```python
from functools import lru_cache
import weakref

class CachedService:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
    
    @lru_cache(maxsize=128)
    def expensive_computation(self, input_data: str) -> str:
        """결과를 캐시하는 비용이 큰 연산"""
        # 복잡한 계산
        return result
    
    async def get_with_cache(self, key: str):
        """약한 참조를 사용한 캐시"""
        if key in self._cache:
            return self._cache[key]
        
        result = await self._compute_result(key)
        self._cache[key] = result
        return result
```

### 3. 데이터베이스 최적화

```python
class OptimizedRepository:
    async def batch_insert(self, items: list[dict]):
        """배치 삽입으로 성능 향상"""
        query = """
            INSERT INTO table_name (col1, col2) 
            VALUES ($1, $2)
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.executemany(query, [
                (item['col1'], item['col2']) for item in items
            ])
    
    async def paginated_query(self, offset: int, limit: int):
        """페이지네이션으로 메모리 사용량 제한"""
        query = """
            SELECT * FROM large_table 
            ORDER BY id 
            OFFSET $1 LIMIT $2
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, offset, limit)
            return [dict(row) for row in rows]
```

### 4. BM25 검색 캐시

- **목적**: 애플리케이션의 빠른 시작을 위해, BM25 검색 모델을 미리 계산하여 파일로 저장합니다.
- **파일 위치**: `data/preprocessed/bm25_cache.pkl`
- **자동 생성**: 이 캐시 파일이 없을 경우, 서버가 처음 시작될 때 자동으로 생성됩니다. 
  - **주의**: 최초 생성 시에는 약 45,000개의 판례를 처리하므로 **수 분의 시간**이 소요될 수 있습니다.
- **수동 갱신**: 소스 판례 데이터(`data/preprocessed/` 내의 JSON 파일들)가 변경된 경우, `bm25_cache.pkl` 파일을 **수동으로 삭제**해야 합니다. 삭제 후 서버를 재시작하면 캐시가 자동으로 다시 생성됩니다.

---

## 📚 관련 문서

- [API 문서](API.md)
- [테스트 가이드](TESTING.md)
- [배포 가이드](DEPLOYMENT.md)
- [아키텍처 가이드](ARCHITECTURE.md)