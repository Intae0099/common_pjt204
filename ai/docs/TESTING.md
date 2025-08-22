# 🧪 테스트 가이드

ALaw AI-Backend의 테스트 작성 및 실행 가이드입니다.

## 📋 목차

- [테스트 개요](#테스트-개요)
- [테스트 환경 설정](#테스트-환경-설정)
- [테스트 실행](#테스트-실행)
- [테스트 작성](#테스트-작성)
- [커버리지 분석](#커버리지-분석)
- [성능 테스트](#성능-테스트)
- [모킹 가이드](#모킹-가이드)

---

## 테스트 개요

### 테스트 전략

1. **단위 테스트 (Unit Tests)**: 개별 함수/클래스 테스트
2. **통합 테스트 (Integration Tests)**: 여러 컴포넌트 간 상호작용 테스트
3. **API 테스트**: REST API 엔드포인트 테스트
4. **성능 테스트**: 응답 시간 및 부하 테스트

### 테스트 구조

```
tests/
├── conftest.py              # 공통 픽스처 및 설정
├── test_api_integration.py  # API 통합 테스트
├── test_exceptions.py       # 예외 처리 테스트
├── test_performance.py      # 성능 테스트
├── test_queue_system.py     # 큐 시스템 테스트
└── services/                # 서비스별 테스트
    ├── test_search_service.py
    ├── test_case_analysis_service.py
    └── test_chat_service.py
```

---

## 테스트 환경 설정

### 1. 의존성 설치

```bash
# 개발 의존성 설치 (테스트 도구 포함)
pip install -r requirements-dev.txt
```

### 2. 테스트 설정 파일

**pytest.ini**:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### 3. 환경 변수 설정

```bash
# 테스트용 환경 변수
export TESTING=true
export DATABASE_URL=postgresql://postgres:test@localhost:5432/alaw_ai_test
export LOG_LEVEL=WARNING
```

---

## 테스트 실행

### 기본 실행

```bash
# 전체 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/test_search_service.py

# 특정 테스트 함수 실행
pytest tests/test_search_service.py::test_vector_search

# 특정 클래스의 모든 테스트
pytest tests/test_api_integration.py::TestAPIIntegration
```

### 마커 기반 실행

```bash
# 단위 테스트만 실행
pytest -m unit

# 통합 테스트만 실행
pytest -m integration

# 느린 테스트 제외
pytest -m "not slow"
```

### 병렬 실행

```bash
# pytest-xdist 사용 (4개 프로세스)
pytest -n 4

# 자동으로 CPU 코어 수만큼 병렬 실행
pytest -n auto
```

### 상세 옵션

```bash
# 실패 시 즉시 중단
pytest -x

# 실패한 테스트만 재실행
pytest --lf

# 가장 느린 10개 테스트 표시
pytest --durations=10

# 실시간 출력
pytest -s
```

---

## 테스트 작성

### 1. 기본 테스트 구조

```python
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

class TestSearchService:
    """검색 서비스 테스트 클래스"""
    
    @pytest.fixture
    def search_service(self, mock_embedding_model, mock_cross_encoder_model):
        """테스트용 검색 서비스 인스턴스"""
        return SearchService(mock_embedding_model, mock_cross_encoder_model)
    
    @pytest.mark.asyncio
    async def test_vector_search_success(self, search_service):
        """벡터 검색 성공 테스트"""
        # Given
        query = "계약 위반"
        expected_results = [{"case_id": "123", "title": "계약 위반 사례"}]
        
        # When
        with patch('services.search_service.get_psycopg2_connection') as mock_conn:
            mock_conn.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = expected_results
            results, total = await search_service.vector_search(query)
        
        # Then
        assert len(results) > 0
        assert total >= len(results)
        assert all('case_id' in result for result in results)
```

### 2. 픽스처 활용

```python
# conftest.py
@pytest.fixture
def mock_database_connection():
    """모의 데이터베이스 연결"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn, mock_cursor

@pytest.fixture
def sample_legal_case():
    """샘플 법률 케이스 데이터"""
    return {
        "case_id": "2000다12345",
        "title": "계약 위반에 따른 손해배상청구",
        "decision_date": "2000-01-01",
        "category": "민사",
        "summary": "계약을 위반한 피고에게 손해배상을 청구한 사건"
    }

# 테스트에서 사용
def test_case_processing(sample_legal_case):
    processor = CaseProcessor()
    result = processor.process(sample_legal_case)
    assert result['processed'] == True
```

### 3. 비동기 테스트

```python
@pytest.mark.asyncio
async def test_async_service():
    """비동기 서비스 테스트"""
    service = AsyncService()
    
    # 비동기 함수 테스트
    result = await service.process_async("input")
    assert result == "expected"
    
    # 여러 비동기 작업 테스트
    tasks = [service.process_async(f"input_{i}") for i in range(3)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 3
```

### 4. 예외 테스트

```python
def test_validation_error():
    """유효성 검증 오류 테스트"""
    service = ValidationService()
    
    with pytest.raises(ValidationError) as exc_info:
        service.validate("")
    
    assert "입력값이 비어있습니다" in str(exc_info.value)
    assert exc_info.value.details['field'] == 'input'

@pytest.mark.asyncio
async def test_database_error_handling():
    """데이터베이스 오류 처리 테스트"""
    service = SearchService()
    
    with patch('services.search_service.get_psycopg2_connection', side_effect=psycopg2.Error("DB Error")):
        with pytest.raises(DatabaseError) as exc_info:
            await service.vector_search("test")
        
        assert "데이터베이스 오류" in str(exc_info.value)
```

### 5. 파라미터화 테스트

```python
@pytest.mark.parametrize("query,expected_count", [
    ("계약", 5),
    ("손해배상", 3),
    ("민사", 10),
    ("", 0),  # 빈 쿼리
])
def test_search_with_various_queries(query, expected_count):
    """다양한 쿼리로 검색 테스트"""
    service = SearchService()
    results = service.search(query)
    assert len(results) == expected_count

@pytest.mark.parametrize("invalid_input", [
    None,
    "",
    "a",  # 너무 짧음
    "x" * 1000,  # 너무 김
])
def test_invalid_inputs(invalid_input):
    """잘못된 입력값 테스트"""
    service = ValidationService()
    with pytest.raises(ValidationError):
        service.validate(invalid_input)
```

---

## 커버리지 분석

### 1. 커버리지 실행

```bash
# 커버리지 측정과 함께 테스트 실행
coverage run -m pytest

# 커버리지 리포트 출력
coverage report

# HTML 리포트 생성
coverage html

# 특정 모듈만 커버리지 측정
coverage run --source=services -m pytest
```

### 2. 커버리지 설정

**.coveragerc**:
```ini
[run]
source = .
omit = 
    */venv/*
    */tests/*
    */migrations/*
    */__pycache__/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    
[html]
directory = htmlcov
```

### 3. 커버리지 목표

- **전체 코드**: 80% 이상
- **핵심 서비스**: 90% 이상
- **API 엔드포인트**: 85% 이상

---

## 성능 테스트

### 1. 응답 시간 테스트

```python
import time
import pytest

class TestPerformance:
    @pytest.mark.asyncio
    async def test_search_response_time(self, search_service):
        """검색 응답 시간 테스트"""
        start_time = time.time()
        results, total = await search_service.vector_search("계약 분쟁", size=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 응답 시간이 2초 이내인지 확인
        assert response_time < 2.0, f"응답 시간이 너무 느림: {response_time:.2f}초"
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, search_service):
        """동시 요청 처리 성능 테스트"""
        async def single_request():
            return await search_service.vector_search("테스트", size=5)
        
        # 10개 동시 요청
        start_time = time.time()
        tasks = [single_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        assert total_time < 5.0, f"동시 요청 처리가 너무 느림: {total_time:.2f}초"
        assert len(results) == 10
```

### 2. 메모리 사용량 테스트

```python
import psutil
import gc

def test_memory_usage():
    """메모리 사용량 테스트"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # 메모리를 많이 사용하는 작업
    service = HeavyService()
    service.process_large_data()
    
    # 가비지 컬렉션 강제 실행
    gc.collect()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 메모리 증가량이 100MB 이하인지 확인
    assert memory_increase < 100 * 1024 * 1024, f"메모리 사용량이 너무 큼: {memory_increase} bytes"
```

### 3. 부하 테스트

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.slow
@pytest.mark.asyncio
async def test_load_capacity():
    """부하 용량 테스트"""
    service = SearchService()
    
    async def simulate_user_request():
        await service.vector_search("부하 테스트", size=5)
    
    # 100명 동시 사용자 시뮬레이션
    tasks = [simulate_user_request() for _ in range(100)]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    
    # 성공률 확인
    successful_requests = [r for r in results if not isinstance(r, Exception)]
    success_rate = len(successful_requests) / len(results)
    
    assert success_rate > 0.95, f"성공률이 너무 낮음: {success_rate:.2%}"
    
    # 전체 처리 시간 확인
    total_time = end_time - start_time
    assert total_time < 30.0, f"부하 처리 시간이 너무 김: {total_time:.2f}초"
```

---

## 모킹 가이드

### 1. 기본 모킹

```python
from unittest.mock import MagicMock, patch

def test_with_basic_mock():
    """기본 모킹 사용"""
    # Mock 객체 생성
    mock_service = MagicMock()
    mock_service.get_data.return_value = {"test": "data"}
    
    # Mock을 사용하는 코드 테스트
    processor = DataProcessor(mock_service)
    result = processor.process()
    
    # Mock 호출 확인
    mock_service.get_data.assert_called_once()
    assert result == {"processed": True}

@patch('module.external_service')
def test_with_patch(mock_external):
    """패치 데코레이터 사용"""
    mock_external.fetch_data.return_value = "mocked_data"
    
    service = MyService()
    result = service.process()
    
    mock_external.fetch_data.assert_called_once()
    assert result == "processed_mocked_data"
```

### 2. 비동기 모킹

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_mock():
    """비동기 함수 모킹"""
    mock_async_service = AsyncMock()
    mock_async_service.async_method.return_value = "async_result"
    
    service = MyAsyncService(mock_async_service)
    result = await service.process()
    
    mock_async_service.async_method.assert_awaited_once()
    assert result == "processed_async_result"

@pytest.mark.asyncio
async def test_async_context_manager():
    """비동기 컨텍스트 매니저 모킹"""
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()
    mock_conn.__aenter__.return_value = mock_cursor
    
    with patch('services.database.get_connection', return_value=mock_conn):
        service = DatabaseService()
        result = await service.query("SELECT * FROM table")
        
        mock_conn.__aenter__.assert_awaited_once()
        assert result is not None
```

### 3. 복잡한 모킹 시나리오

```python
def test_complex_mocking():
    """복잡한 모킹 시나리오"""
    # 여러 단계의 모킹
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor
    
    # 순차적 반환값 설정
    mock_cursor.fetchone.side_effect = [
        ("result1",),
        ("result2",),
        None  # 마지막은 None
    ]
    
    # 예외 발생 시뮬레이션
    mock_cursor.execute.side_effect = [
        None,  # 첫 번째 호출은 성공
        DatabaseError("Connection failed")  # 두 번째 호출은 실패
    ]
    
    service = DatabaseService(mock_db)
    
    # 첫 번째 호출 - 성공
    result1 = service.query("SELECT 1")
    assert result1 == "result1"
    
    # 두 번째 호출 - 실패
    with pytest.raises(DatabaseError):
        service.query("SELECT 2")
```

### 4. 외부 API 모킹

```python
@patch('requests.get')
def test_external_api_call(mock_get):
    """외부 API 호출 모킹"""
    # Mock 응답 설정
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "data": "test"}
    mock_get.return_value = mock_response
    
    client = ExternalAPIClient()
    result = client.fetch_data("test_id")
    
    # 호출 확인
    mock_get.assert_called_once_with(
        "https://api.example.com/data/test_id",
        headers={"Authorization": "Bearer token"}
    )
    assert result == {"status": "success", "data": "test"}

@patch('openai.OpenAI')
def test_llm_client(mock_openai):
    """LLM 클라이언트 모킹"""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "모킹된 AI 응답"
    mock_client.chat.completions.create.return_value = mock_response
    
    llm_service = LLMService()
    result = llm_service.generate_response("테스트 프롬프트")
    
    assert result == "모킹된 AI 응답"
    mock_client.chat.completions.create.assert_called_once()
```

---

## CI/CD 통합

### GitHub Actions 예시

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=services --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## 📚 관련 문서

- [개발 가이드](DEVELOPMENT.md)
- [API 문서](API.md)
- [배포 가이드](DEPLOYMENT.md)
- [아키텍처 가이드](ARCHITECTURE.md)