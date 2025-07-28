# AI 서비스 모듈 README

## 1. 개요
이 레포지토리는 ‘미정’ AI 기반 화상 법률 상담 플랫폼 중 **AI 파트**만을 담당합니다.  
LLM(LLM + LangChain)을 활용한 사전 상담 문서 자동 생성, 판례·법령 검색, 법률 분석, 챗봇 응답의 핵심 로직을 포함합니다.

---

## 2. 폴더 구조

```

legal-ai-platform/
│
├── app/                    # FastAPI 엔트리 & 라우터
│   ├── main.py             # 서버 실행, 전역 미들웨어
│   └── routes.py           # 단일 라우터 모듈 (v1)
│
├── services/               # 비즈니스 서비스 (기능 1:1 대응)
│   ├── structuring.py      # 2‑1 사건 구조화
│   ├── analysis.py         # 3‑1~3‑4 법률 분석
│   ├── application.py      # 4‑X 상담 신청서
│   ├── search.py           # 5·6 판례·법령 검색
│   └── chat.py             # 7 챗봇
│
├── llm/                    # LLM & RAG 계층
│   ├── model.py            # OpenAI 싱글턴
│   ├── prompts.py          # 모든 프롬프트 정의
│   ├── chains.py           # LangChain 체인 래퍼
│   └── chroma.py           # ChromaDB 초기화·검색 Helper
│
├── db/                     # ORM & 마이그레이션
│   ├── models.py           # SQLAlchemy ORM
│   └── alembic/            # (필요 시) 마이그레이션 스크립트
│
├── scripts/                # CLI 유틸
│   ├── preprocess_cases.py # 원본 → 정제
│   └── build_index.py      # Chroma 인덱스 재생성
│
├── tests/                  # **Service 계층 전용 테스트**
│   └── test_*.py
│
├── data/                   # raw / processed / chroma_index
└── README.md

````

---

## 3. API 응답 규격

### 성공 응답

```json
{
  "success": true,
  "data": { ... }
}
```

### 실패 응답

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지"
  },
  "details": { ... } // (선택적) 상세 정보
}
```

### 공통 오류 코드

| 코드 | 설명 |
|---|---|
| `INVALID_PARAM` | 필수 값 누락, 형식 오류 등 |
| `UNAUTHORIZED` | 토큰 없음, 만료, 권한 부족 |
| `NOT_FOUND` | 요청한 리소스를 찾을 수 없음 |
| `SERVER_ERROR` | 예기치 못한 서버 오류 |

---

## 4. 설치 & 실행

1. Conda 환경 생성  
   ```bash
   conda env create -f environment.yml
   conda activate legal-ai-platform
    ```

2. `.env` 파일 설정

   ```
   OPENAI_API_KEY=your_key
   CHROMA_DB_PATH=/path/to/chroma_index
   ```
3. 인덱스 초기화 (최초 1회)

   ```bash
   python scripts/build_index.py
   ```
4. FastAPI 실행

   ```bash
   uvicorn app.main:app --reload
   ```

   — AI 서비스는 `/api/v1/…` 엔드포인트를 통해 호출합니다.

---

## 5. 테스트

```bash
pytest tests/
```

* **서비스 계층** 함수 단위로 성공/예외 흐름만 검증합니다.
* 외부 호출(OpenAI, ChromaDB, DB)은 `pytest-mock` 으로 모킹하세요.

---
