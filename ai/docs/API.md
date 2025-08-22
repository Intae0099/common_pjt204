# 🔧 API 문서

ALaw AI-Backend의 REST API 엔드포인트 가이드입니다.

## 📋 목차

- [기본 정보](#기본-정보)
- [인증](#인증)
- [케이스 분석 API](#케이스-분석-api)
- [검색 API](#검색-api)
- [챗봇 API](#챗봇-api)
- [구조화 API](#구조화-api)
- [상담 API](#상담-api)
- [큐 시스템 API](#큐-시스템-api)
- [에러 응답](#에러-응답)

---

## 기본 정보

### Base URL
- **로컬**: `http://localhost:8000`
- **프로덕션**: `http://122.38.210.80:8997`

### Content-Type
모든 요청에서 `Content-Type: application/json`을 사용합니다.

### API 버전
현재 버전: `v1` (URL에 버전 명시 없음)

---

## 인증

> **참고**: 현재 인증 시스템이 제거되어 모든 API는 인증 없이 사용 가능합니다.

---

## 케이스 분석 API

### 📊 케이스 분석 요청

**POST** `/api/analysis`

사용자의 사건 내용을 AI로 분석하여 법적 쟁점과 관련 판례를 제공합니다.

#### 요청 예시
```json
{
    "case": {
        "fullText": "계약을 체결했으나 상대방이 이행하지 않아 피해를 입었습니다."
    },
    "recommend_lawyers": true
}
```

#### 응답 예시
```json
{
    "success": true,
    "data": {
        "report": {
            "case_analysis": {
                "legal_issues": ["계약 위반", "손해배상"],
                "analysis": "계약 불이행으로 인한 손해배상 청구 사안입니다...",
                "confidence": 0.85,
                "statutes": ["민법 제390조", "제393조"],
                "similar_cases": [
                    {
                        "case_id": "2000다12345",
                        "title": "계약 위반에 따른 손해배상",
                        "similarity": 0.92
                    }
                ]
            }
        }
    }
}
```

---

## 검색 API

### 🔍 판례 검색

**GET** `/api/search/cases`

키워드로 관련 판례를 검색합니다.

#### 쿼리 파라미터
- `keyword` (required): 검색 키워드 (최소 2자)
- `page` (optional, default=1): 페이지 번호
- `size` (optional, default=10): 페이지당 결과 수 (최대 50)

#### 요청 예시
```bash
GET /api/search/cases?keyword=계약&page=1&size=10
```

#### 응답 예시
```json
{
    "data": {
        "items": [
            {
                "case_id": "2000다12345",
                "title": "계약 위반에 따른 손해배상청구",
                "decision_date": "2000-01-01",
                "category": "민사",
                "summary": "계약 불이행으로 인한 분쟁"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_items": 50,
            "items_per_page": 10
        }
    }
}
```

### 📖 판례 상세 조회

**GET** `/api/cases/{case_id}`

특정 판례의 상세 정보를 조회합니다.

#### 응답 예시
```json
{
    "success": true,
    "data": {
        "caseId": "2000다12345",
        "title": "계약 위반에 따른 손해배상청구",
        "decisionDate": "2000-01-01",
        "category": "민사",
        "issue": "계약 위반",
        "summary": "계약을 위반한 피고에게 손해배상을 청구한 사건",
        "fullText": "원고는 피고와 계약을 체결하였으나...",
        "statutes": "민법 제390조, 제393조",
        "precedents": "대법원 1999다12345 판결"
    }
}
```

---

## 챗봇 API

### 💬 채팅 스트림

**POST** `/api/ai/chat/stream`

실시간 스트리밍 방식으로 AI 챗봇과 대화합니다.

#### 요청 예시
```json
{
    "message": "계약 위반 시 손해배상 청구 방법을 알려주세요."
}
```

#### 응답 (Server-Sent Events)
```
data: {"reply": "계약 위반 시 손해배상을 청구하는 방법은 다음과 같습니다.\n\n"}
data: {"reply": "1. 계약서 검토\n"}
data: {"reply": "2. 손해 산정\n"}
data: {"reply": "3. 내용증명 발송\n"}
```

---

## 구조화 API

### 📝 사건 구조화

**POST** `/api/cases/structuring`

자유 형식의 텍스트를 법률 사건 구조로 변환합니다.

#### 요청 예시
```json
{
    "freeText": "작년에 계약을 맺었는데 상대방이 돈을 주지 않아서 문제가 생겼습니다."
}
```

#### 응답 예시
```json
{
    "case": {
        "title": "계약금 미지급 사건",
        "summary": "계약 체결 후 상대방의 대금 미지급으로 인한 분쟁",
        "fullText": "당사자들은 작년에 계약을 체결하였으나, 상대방이 약정된 대금을 지급하지 않아 분쟁이 발생하였습니다."
    }
}
```

---

## 상담 API

### 📋 상담 신청서 생성

**POST** `/api/consult/application`

분석된 사건 정보를 바탕으로 상담 신청서를 생성합니다.

#### 요청 예시
```json
{
    "case_analysis": {
        "legal_issues": ["계약 위반"],
        "analysis": "계약 불이행 사안",
        "statutes": ["민법 제390조"]
    },
    "user_info": {
        "name": "홍길동",
        "phone": "010-1234-5678",
        "email": "hong@example.com"
    }
}
```

#### 응답 예시
```json
{
    "success": true,
    "data": {
        "application": {
            "title": "계약 위반 상담 신청",
            "content": "구조화된 상담 신청서 내용...",
            "questions": [
                "계약서 원본을 보유하고 계신지요?",
                "상대방과의 연락은 언제까지 이어졌나요?"
            ]
        }
    }
}
```

---

## 큐 시스템 API

### 📊 큐 상태 조회

**GET** `/api/queue/status`

큐 시스템의 현재 상태를 HTML 형태로 조회합니다.

#### 응답
HTML 대시보드 페이지

### 📊 큐 상태 JSON

**GET** `/api/queue/status/json`

큐 시스템의 현재 상태를 JSON 형태로 조회합니다.

#### 응답 예시
```json
{
    "is_running": true,
    "queue_stats": {
        "search": {
            "pending": 0,
            "processing": 1,
            "completed": 10
        }
    },
    "processing_count": {
        "search": 1
    },
    "resource_usage": {
        "memory_percent": 50,
        "cpu_percent": 30
    }
}
```

### 💚 헬스체크

**GET** `/api/queue/health`

큐 시스템의 헬스 상태를 확인합니다.

#### 응답 예시
```json
{
    "status": "healthy",
    "is_running": true,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 에러 응답

### 표준 에러 형식

모든 에러는 다음 형식으로 응답됩니다:

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "요청 데이터가 유효하지 않습니다.",
        "details": {
            "field": "keyword",
            "reason": "키워드는 최소 2자 이상이어야 합니다."
        }
    }
}
```

### 주요 에러 코드

| 코드 | 설명 | HTTP 상태 |
|------|------|-----------|
| `VALIDATION_ERROR` | 입력 데이터 검증 실패 | 400 |
| `NOT_FOUND` | 리소스를 찾을 수 없음 | 404 |
| `DATABASE_ERROR` | 데이터베이스 오류 | 500 |
| `LLM_ERROR` | AI 모델 처리 오류 | 500 |
| `SEARCH_ERROR` | 검색 처리 오류 | 500 |
| `QUEUE_FULL` | 큐가 가득 참 | 503 |

---

## 📝 추가 정보

### 응답 시간
- **일반 검색**: 평균 1-3초
- **AI 분석**: 평균 10-30초
- **챗봇 스트림**: 첫 응답 1초 내

### 요청 제한
- **동시 처리**: 큐 시스템을 통한 자동 제어
- **페이지 크기**: 최대 50개 항목
- **키워드 길이**: 2-100자

### 지원 형식
- **입력**: JSON, UTF-8 인코딩
- **출력**: JSON, Server-Sent Events (채팅)

---

**📚 관련 문서**
- [아키텍처 가이드](ARCHITECTURE.md)
- [개발 가이드](DEVELOPMENT.md)
- [테스트 가이드](TESTING.md)