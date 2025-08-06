
# CLAUDE.md

이 파일은 이 리포지토리에서 코드 작업을 할 때 Claude Code(claude.ai/code)에 대한 가이드를 제공합니다.

## 개발 명령

### 환경 설정
```bash
# Conda 환경 생성 및 활성화
conda env create -f environment.yml
conda activate legal-ai-platform

# Python 의존성 설치
pip install -r requirements.txt
```

### 환경 구성

`config/.env.example` 파일을 `config/.env`로 복사한 후 다음을 설정하세요:

* `GMS_KEY`: GPT-4o 모델용 OpenAI API 키
* 데이터베이스 연결 파라미터: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`

### 데이터베이스 설정

```bash
# pgvector 확장 포함 PostgreSQL 시작
cd db
docker-compose up -d
```

### 애플리케이션 실행

```bash
# FastAPI 개발 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 모듈 실행
pytest tests/api/
pytest tests/services/
pytest tests/llm/

# 상세 출력 옵션
pytest -v
```

## 아키텍처 개요

### 핵심 서비스 아키텍처

이 시스템은 **법률 AI 플랫폼 백엔드**로, FastAPI를 사용하여 AI 기반 법률 사례 분석 및 상담 기능을 제공합니다. 계층화된 서비스 지향 아키텍처를 따르고 있습니다.

**주요 서비스** (`services/` 디렉터리):

* `StructuringService`: 비정형 사례 텍스트를 LLM으로 구조화된 법률 사례 요약으로 변환
* `SearchService`: 임베딩 + 교차 인코더 재순위화를 이용한 벡터 유사도 검색
* `CaseAnalysisService`: 검색된 판례와 GPT-4o 추론을 결합한 RAG 기반 법률 분석
* `ConsultationService`: 공식 상담 신청서와 변호사용 질문 자동 생성
* `ChatService`: SSE 스트리밍 응답을 지원하는 실시간 법률 채팅

### 데이터 흐름 아키텍처

1. **사례 구조화**: 자유 텍스트 → LLM → 구조화된 사례 요약
2. **법률 검색**: 질의 → 임베딩 생성 → 벡터 DB → 교차 인코더 재순위화 → 관련 판례 도출
3. **사례 분석**: 구조화된 사례 + 검색 판례 → RAG 파이프라인 → 판례 인용 법률 분석
4. **상담 신청**: 분석 결과 → 템플릿 생성 → 상담 신청 문서

### AI/ML 컴포넌트 (`llm/` 디렉터리)

* **모델 로딩**: `ModelLoader` 싱글턴 패턴으로 임베딩 & 교차 인코더 모델 캐싱
* **임베딩 모델**: sentence-transformers 기반 벡터 검색
* **교차 인코더**: 검색 후보 재순위화
* **LLM 통합**: LangChain과 OpenAI GPT-4o 연동
* **파서**: LLM 응답의 구조화된 출력 추출용 커스텀 파서

### 데이터베이스 아키텍처

* **PostgreSQL** + **pgvector** 확장 사용
* 판례 메타데이터와 벡터 임베딩을 함께 저장
* SQLAlchemy를 통한 비동기 연결
* `db/database.py`에서 커넥션 풀링 관리

### API 구조 (`app/api/`)

* **FastAPI**: 비동기 요청 처리
* **예외 처리**: 표준화된 오류 응답
* **CORS 미들웨어**: 프론트엔드 통합 지원
* **앱 수명주기 이벤트**: 시작 시 모델 프리로딩
* **SSE 스트리밍**: 실시간 채팅 응답 지원

## 주요 구현 세부사항

### 리팩토링된 아키텍처 (2024.08)

**중앙화된 설정 관리**:
* `config/settings.py`: Pydantic 기반 타입 안전한 설정 관리
* 환경별 설정 분리 (데이터베이스, LLM, API, 검색, 로깅)
* 싱글톤 패턴으로 설정 인스턴스 제공

**의존성 주입 시스템**:
* `core/container.py`: 간단한 DI 컨테이너 구현
* 서비스 간 느슨한 결합도 달성
* 팩토리 패턴과 싱글톤 패턴 혼합 사용

**표준화된 예외 처리**:
* `utils/exceptions.py`: 계층별 커스텀 예외 클래스
* 데코레이터 기반 자동 예외 처리
* 구조화된 에러 정보 제공

**통합 로깅 시스템**:
* `utils/logger.py`: 중앙화된 로깅 설정
* LoggerMixin으로 일관된 로깅 패턴
* 실행 시간 측정 데코레이터 제공

**API 응답 표준화**:
* `app/api/response_models.py`: 일관된 응답 구조
* `app/api/decorators.py`: 공통 예외 처리 및 검증
* 페이지네이션 표준화

### 벡터 검색 파이프라인

2단계 검색을 구현:
1. **임베딩 유사도 검색** (Faiss 활용)
2. **교차 인코더 재순위화**

### LLM 응답 처리

* **구조화된 파싱**: 설정 기반 재시도 로직
* **Chain of Thought(CoT) 프롬프트**: 법률 추론 명확화
* **커스텀 출력 파서**: LLM 출력에서 구조화 데이터 추출

### 환경 변수 구성

* `config/settings.py`에서 중앙 관리
* Pydantic BaseSettings로 타입 검증
* 환경변수와 기본값 설정 통합

### 테스트 구조

* **API 테스트**: 통합된 응답 모델 테스트
* **서비스 테스트**: 의존성 주입 기반 단위 테스트
* **LLM 테스트**: 모듈화된 컴포넌트 테스트
* **비동기 테스트 설정**: `pytest.ini`에 `asyncio_mode = auto`

## 개발 노트

* **설정 우선순위**: 환경변수 > .env 파일 > 기본값
* **의존성 주입**: `core.container.inject()` 사용
* **로깅**: 각 서비스는 `LoggerMixin` 상속
* **예외 처리**: `@handle_service_exceptions` 데코레이터 활용
* **API 응답**: `@handle_api_exceptions` 데코레이터로 통일
* 한국어 법률 도메인 지원 전체 적용

## 리팩토링 개선사항

### 가독성 향상
* 중복 import 문 제거
* 하드코딩된 설정값을 환경변수로 분리
* 일관된 네이밍 컨벤션 적용

### 유지보수성 증대
* 중앙화된 설정 관리로 변경 포인트 최소화
* 의존성 주입으로 테스트 가능성 향상
* 표준화된 에러 핸들링

### 중복코드 제거
* 공통 응답 처리 로직 추상화
* 재사용 가능한 데코레이터 패턴
* 통합된 로깅 유틸리티

### 확장성 확보
* 새로운 서비스 추가 시 DI 컨테이너에 등록만 필요
* 설정 기반 동적 구성
* 플러그인 아키텍처 준비

