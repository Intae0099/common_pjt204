# ALaw AI-Backend

> AI 기반 화상 법률 상담 플랫폼 'ALaw'의 핵심 AI 백엔드 서비스입니다.

본 리포지토리는 사용자의 사건 개요를 분석하고, 법률 정보를 검색하며, 변호사와의 상담을 효율적으로 지원하는 AI 기반 API 서버의 소스 코드를 관리합니다.

---

## 1. 프로젝트 개요

ALaw 플랫폼은 법률 상담의 진입장벽을 낮추기 위해 기획되었습니다. 그중 AI 백엔드는 복잡한 법률 문제를 기술적으로 해결하는 핵심 엔진 역할을 수행합니다. 사용자가 입력한 자연어 형태의 사건 내용을 구조화하고, 방대한 판례 데이터베이스에서 유사 사례를 찾아내며, 법률적 쟁점을 분석하여 초기 법률 소견까지 제공하는 것을 목표로 합니다.

## 2. 핵심 기능 (Features)

- **사건 구조화 AI**: 사용자의 사건 개요(자유 텍스트)를 LLM과의 대화를 통해 법률적으로 유의미한 표준 스키마(사건 경위서)로 정제합니다. (`services/structuring_service.py`)
- **AI 법률 분석**:
    - **유사 판례/법령 검색**: 구조화된 사건을 기반으로 벡터 DB에서 관련성 높은 판례 및 법령을 검색하고, Cross-encoder로 재정렬하여 정확도를 높입니다. (`services/search_service.py`)
    - **법률 쟁점 도출 및 초기 법률 소견 제공**: 검색된 자료와 사건 경위서를 `LangChain`과 `GPT-4o`를 이용해 종합, 법률적 쟁점을 분석하고 초기 법률 소견을 생성합니다. (`services/case_analysis_service.py`)
- **상담 신청서 생성 AI**: 분석된 사건 내용과 사용자 추가 정보를 결합하여 정형화된 상담 신청서를 생성하고, 변호사를 위한 핵심 질문을 자동으로 도출합니다. (`services/consultation_service.py`)
- **실시간 법률 챗봇**: `FastAPI`의 SSE(Server-Sent Events)를 활용하여 법률 도메인 특화 AI 챗봇과의 실시간 스트리밍 대화를 지원합니다. (`services/chat_service.py`)

## 3. 기술 스택 (Tech Stack)

- **Language**: Python 3.10+
- **Framework**: FastAPI, Pydantic
- **AI & LLM**: LangChain, OpenAI GPT-4o, Sentence-Transformers
- **API & Database**: SQLAlchemy, PostgreSQL
- **Testing**: Pytest
- **Deployment**: Docker, Uvicorn

## 4. 설치 및 실행 방법 (Getting Started)

### 4.1. 사전 요구사항

- Python 3.10 이상
- Conda 또는 venv 가상 환경

### 4.2. 설치 (Conda)

1.  **리포지토리 클론**
    ```bash
    git clone https://github.com/your-repo/ALaw-AI-Backend.git
    cd ALaw-AI-Backend
    ```

2.  **Conda 가상환경 생성 및 활성화**
    `environment.yml` 파일을 사용하여 Conda 환경을 생성하고 활성화합니다.
    ```bash
    conda env create -f environment.yml
    conda activate alaw-ai
    ```

3.  **환경 변수 설정**
    `config/.env.example` 파일을 `config/.env`로 복사하고, 내부에 OpenAI API 키 등 필요한 환경 변수를 설정합니다.

### 4.3. 로컬 서버 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4.4. Docker를 이용한 배포

현재 프로젝트는 완전한 Docker 기반 배포 환경을 지원합니다.

#### 📦 **로컬 Docker 배포**

1.  **환경변수 설정**
    ```bash
    cp config/.env.example config/.env
    # config/.env 파일 편집하여 API 키 등 설정
    ```

2.  **데이터베이스 실행**
    ```bash
    cd db
    docker-compose up -d
    ```

3.  **AI 애플리케이션 배포**
    ```bash
    cd docker
    docker-compose up -d --build
    ```

4.  **서비스 확인**
    ```bash
    # 애플리케이션 상태 확인
    curl http://localhost:8997/
    
    # 로그 확인
    docker-compose logs -f ai-app
    ```

#### 🚀 **프로덕션 배포**

**배포 URL**: [http://122.38.210.80:8997/](http://122.38.210.80:8997/)

- **포트**: 8997 (외부) → 8000 (내부)
- **자동 재시작**: `restart: always` 설정
- **볼륨 마운트**: 데이터 및 로그 영구 저장
- **네트워크**: `db_default` 네트워크로 데이터베이스 연결

## 5. CI/CD 및 자동 배포

프로젝트는 **GitLab CI/CD**를 통한 완전 자동화된 배포 시스템을 갖추고 있습니다.

- **자동 배포**: `dev-AI` 브랜치 Push 시 자동 실행
- **배포 시간**: 15-20분 (AI 모델 로딩 포함)
- **실시간 알림**: Mattermost를 통한 배포 결과 알림
- **스마트 헬스체크**: AI 모델 로딩 완료까지 자동 대기

📖 **상세 가이드**: [CI/CD 가이드 문서](docs/CICD_GUIDE.md)

## 6. 테스트 방법 (Test)

프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 모든 테스트를 수행할 수 있습니다.

```bash
pytest
```

## 6. 운영 및 모니터링

**배포 URL**: [http://122.38.210.80:8997/](http://122.38.210.80:8997/)

- **서비스 상태**: Docker 컨테이너 기반 모니터링
- **로그 관리**: 일별 로그 파일 자동 생성 및 관리
- **장애 대응**: 자동 재시작 및 롤백 지원
- **성능 최적화**: 리소스 모니터링 및 최적화 가이드

📖 **상세 가이드**: [운영 및 모니터링 문서](docs/OPERATIONS_GUIDE.md)

---

## 7. 시스템 아키텍처

본 프로젝트는 FastAPI 기반의 마이크로서비스 아키텍처를 채택하고 있습니다.

- **API 계층**: FastAPI 라우터를 통한 요청 처리
- **서비스 계층**: 비즈니스 로직별 독립적인 서비스 모듈
- **데이터 계층**: PostgreSQL + FAISS 벡터 DB 하이브리드 구성
- **배포 계층**: Docker 컨테이너 기반 마이크로서비스

📖 **상세 가이드**: [아키텍처 문서](docs/ARCHITECTURE.md)

## 8. 나의 역할 및 기여 (My Role & Contributions)

-   **역할**: AI 백엔드 개발자 + DevOps 엔지니어
-   **주요 책임 및 기여**:
    -   **AI 서비스 API 아키텍처 설계 및 구현**: `FastAPI`를 기반으로 AI 기능들을 모듈화하여 비동기 처리 REST API 서버 전체를 설계하고 구현했습니다. 각 기능은 `services` 디렉토리 내의 서비스 클래스로 분리하여 관리의 용이성을 확보했습니다.
    -   **RAG 파이프라인 구축 및 최적화**: `LangChain`, `Faiss`, `Sentence-Transformers`를 활용하여 유사 판례 검색을 위한 RAG 파이프라인을 구축했습니다. 사용자의 질의를 임베딩하여 벡터 DB에서 유사 문서를 찾고, Cross-Encoder 모델로 재정렬하는 2단계 검색 과정을 구현하여 검색 정확도를 높였습니다.
    -   **LLM 기반 법률 분석 기능 개발**: `OpenAI GPT-4o` 모델과 `LangChain`을 연동하여, 정제된 사건 내용과 검색된 판례를 바탕으로 법률적 쟁점을 도출하고 초기 법률 소견을 생성하는 `CaseAnalysisService`를 개발했습니다.
    -   **실시간 챗봇 스트리밍 구현**: 사용자와의 상호작용을 높이기 위해 `FastAPI`의 Server-Sent Events (SSE)를 활용, `ChatService`에서 LLM의 답변을 토큰 단위로 스트리밍하는 기능을 구현했습니다.
    -   **완전 자동화된 CI/CD 파이프라인 구축**: GitLab CI/CD와 Windows Runner를 활용하여 코드 Push부터 프로덕션 배포까지 완전 자동화된 파이프라인을 구축했습니다. Docker 기반 컨테이너화, 스마트 헬스체크, Mattermost 알림 시스템을 통해 안정적인 배포 환경을 구현했습니다.
    -   **Docker 기반 마이크로서비스 아키텍처**: 애플리케이션과 데이터베이스를 독립적인 Docker 컨테이너로 분리하고, docker-compose를 통한 오케스트레이션으로 확장 가능한 배포 환경을 구축했습니다.
    -   **테스트 자동화**: `Pytest`를 사용하여 각 API 엔드포인트와 서비스 로직에 대한 단위/통합 테스트 코드를 작성(`tests/` 디렉토리)하여 코드의 안정성과 신뢰성을 확보했습니다.

-   **성과**:
    -   **법률 AI 서비스 완전 자동화**: 사건접수 → 분석 → 상담준비 전 과정을 AI로 자동화하는 백엔드 시스템 구축 완료
    -   **무중단 배포 시스템 구현**: 코드 Push부터 프로덕션 반영까지 15-20분 내 완전 자동화된 CI/CD 파이프라인 구축
    -   **확장 가능한 마이크로서비스 아키텍처**: 각 AI 기능을 독립적인 서비스로 분리하여 개별 테스트 및 확장 가능한 구조 설계
    -   **실시간 모니터링 및 알림 시스템**: Mattermost 연동을 통한 실시간 배포 상태 알림 및 장애 감지 시스템 구축

## 9. 현재의 기술적 과제 (Current Challenges)

-   **RAG 정확도 문제**: 특정 법률 용어나 복잡한 사건 맥락에서 관련성이 낮은 판례가 검색되는 경우가 있어, 임베딩 모델의 미세조정(Fine-tuning)이나 하이브리드 검색(키워드+벡터) 도입을 통한 검색 품질 개선이 필요합니다.
-   **임베딩 검색 속도**: `Faiss`를 사용함에도 불구하고 대규모 데이터셋에서 초기 유사 벡터 검색 시 응답 지연이 발생하고 있어, 인덱스 구조 최적화나 근사 탐색(ANN) 파라미터 튜닝이 요구됩니다.
-   **챗봇 대화의 일관성 유지**: 다수의 동시 사용자가 각자의 대화 맥락을 독립적으로 유지하며 일관성 있는 답변을 받도록 현재의 인메모리 기반 대화 기록 방식을 `Redis`와 같은 외부 세션 저장소로 확장하는 방안을 검토 중입니다.
-   **배포 환경 이중화**: 현재 단일 서버 배포 환경을 고가용성(HA) 구성으로 확장하여 무중단 서비스 제공 및 부하 분산 체계 구축이 필요합니다.

## 10. 라이선스 (License)

MIT License

## 11. 작성자 (Author)

-   **GitHub**: [GitHub](https://github.com/grayson1999)
