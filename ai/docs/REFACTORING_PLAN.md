# 🔄 AI 법률 상담 시스템 리팩토링 계획서 (수정안)

## 📋 프로젝트 개요
- **시스템**: FastAPI 기반 AI 법률 상담 서비스
- **주요 기능**: 법률 문서 분석, 검색, 상담, 변호사 추천
- **기술 스택**: FastAPI + PostgreSQL + LLM + 벡터 검색

## 🎯 수정된 리팩토링 우선순위

### 🚨 **Phase 1: 즉시 개선 (High Priority)**
1. **인증 시스템 제거** - 하드코딩된 인증 로직 정리
2. **중복 코드 제거** - builds/ 폴더 완전 삭제
3. **에러 처리 통일** - 예외 처리 표준화

### ⚡ **Phase 2: 성능 개선 (Medium Priority)**  
4. **데이터베이스 최적화** - 쿼리 효율화
5. **테스트 확충** - 단위/통합 테스트

### 🏗️ **Phase 3: 구조 개선 (Low Priority)**
6. **아키텍처 리팩토링** - 의존성 정리
7. **문서화 개선** - README 중심 구조화

## 📝 세부 리팩토링 계획

### **Phase 1: 인증 제거 & 코드 정리 (1-2주)**

#### 1.1 인증 시스템 완전 제거
```python
# 현재: app/api/dependencies.py
def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    return "user"  # 하드코딩

# 개선: 인증 의존성 완전 제거
# - get_current_user 함수 삭제
# - 모든 라우터에서 Depends(get_current_user) 제거
# - 인증 관련 헤더/미들웨어 정리
```

**작업 범위:**
- `app/api/dependencies.py`: get_current_user 함수 삭제
- 모든 라우터 파일: Depends(get_current_user) 제거
- `app/main.py`: 인증 관련 미들웨어 정리
- 관련 import 문 정리

#### 1.2 중복 파일 완전 제거
```bash
# builds/ 폴더 전체 삭제
rm -rf builds/

# .gitignore 업데이트
echo "builds/" >> .gitignore
```

#### 1.3 예외 처리 통일
- 모든 서비스에서 `utils/exceptions.py`의 표준 예외 클래스 사용
- 에러 메시지 한국어 통일
- API 응답 형식 표준화

### **Phase 2: 성능 최적화 (2-3주)**

#### 2.1 메모리 관리 개선
```python
# chat_service.py 개선
from collections import OrderedDict

class ChatService:
    def __init__(self):
        self.chat_histories = OrderedDict()  # LRU 방식
        self.max_sessions = 100
        self.max_history_per_session = 20
    
    def add_message(self, session_id: str, message: dict):
        if len(self.chat_histories) >= self.max_sessions:
            self.chat_histories.popitem(last=False)  # 가장 오래된 세션 삭제
```

#### 2.2 데이터베이스 최적화
```sql
-- 필요한 인덱스 추가
CREATE INDEX CONCURRENTLY idx_cases_content_vector ON cases USING ivfflat(content_vector);
CREATE INDEX CONCURRENTLY idx_statutes_article_number ON statutes(article_number);
CREATE INDEX CONCURRENTLY idx_statutes_content_vector ON statutes USING ivfflat(content_vector);
```

#### 2.3 테스트 코드 확충
- 각 서비스별 단위 테스트 작성
- API 엔드포인트 통합 테스트
- 큐 시스템 성능 테스트

### **Phase 3: 구조 개선 (3-4주)**

#### 3.1 의존성 정리
```txt
# requirements.txt 최적화 (63개 → 45개)
# 사용하지 않는 패키지 제거
# 버전 호환성 검증
```

#### 3.2 문서화 개선 (README 중심)

**새로운 문서 구조:**

```
README.md (간결하고 가독성 높게)
├── 📖 빠른 시작 가이드
├── ⚡ 주요 기능 (핵심만)
├── 🚀 설치 및 실행
├── 📚 상세 문서 (docs/ 링크)
└── 🔧 문제 해결

docs/
├── SETUP.md (환경 설정 통합)
├── API.md (API 문서)
├── ARCHITECTURE.md (기존 유지)
├── OPERATIONS.md (운영 가이드)
└── TROUBLESHOOTING.md (문제 해결)
```

**삭제할 문서:**
- `CLAUDE.md` - Claude 관련 문서 삭제
- `ENV_SETUP_GUIDE.md` - SETUP.md로 통합
- `MODEL_OPTIMIZATION.md` - ARCHITECTURE.md에 통합
- `RAG_EVALUATION_DESIGN.md` - 개발용, 삭제
- `REFACTORING_SUMMARY.md` - 불필요

**새 README.md 구조:**
```markdown
# ALaw AI-Backend

> AI 기반 법률 상담 플랫폼의 핵심 백엔드 서비스

## 🚀 빠른 시작

### 설치
```bash
git clone [repo]
conda env create -f environment.yml
conda activate alaw-ai
```

### 실행
```bash
uvicorn app.main:app --reload
```

## ⚡ 주요 기능
- 🤖 AI 법률 분석
- 🔍 하이브리드 검색
- 💬 실시간 챗봇
- 📊 큐 시스템

## 📚 상세 문서
- [📖 환경 설정](docs/SETUP.md)
- [🏗️ 아키텍처](docs/ARCHITECTURE.md)  
- [🛠️ API 문서](docs/API.md)
- [🚀 운영 가이드](docs/OPERATIONS.md)

## 🔧 문제 해결
- [일반적인 문제](docs/TROUBLESHOOTING.md)
```

## 📊 예상 효과

### **코드 개선**
- 코드 라인 수 25% 감소 (19,322줄 → 14,500줄)
- 중복 코드 완전 제거
- 인증 관련 복잡성 제거

### **성능 개선**
- 메모리 사용량 30% 감소
- 응답 시간 20% 단축
- 데이터베이스 쿼리 최적화

### **문서 개선**
- README 가독성 3배 향상
- 문서 파일 50% 감소 (9개 → 5개)
- 개발자 온보딩 시간 60% 단축

## 🗓️ 실행 일정

| Phase | 작업 | 소요 시간 | 완료 기준 |
|-------|------|-----------|-----------|
| 1 | 인증 제거, 중복 제거, 예외 통일 | 1-2주 | 인증 코드 완전 삭제 |
| 2 | 메모리 최적화, DB 최적화, 테스트 | 2-3주 | 테스트 커버리지 70% |
| 3 | 의존성 정리, 문서 개선 | 1주 | 새 README 완성 |

## 🎯 성공 지표

1. **코드 품질**: 중복 코드 0%, 인증 관련 코드 완전 제거
2. **성능**: 메모리 사용량 30% 감소, 응답시간 < 500ms
3. **문서**: README 길이 50% 단축, 핵심 정보만 포함
4. **테스트**: 단위 테스트 커버리지 > 70%

## 📋 작업 체크리스트

### Phase 1 체크리스트
- [ ] `app/api/dependencies.py`에서 `get_current_user` 함수 삭제
- [ ] 모든 라우터에서 `Depends(get_current_user)` 제거
- [ ] 인증 관련 import 문 정리
- [ ] `builds/` 폴더 완전 삭제
- [ ] `.gitignore`에 `builds/` 추가
- [ ] 모든 서비스에서 표준 예외 클래스 사용 통일
- [ ] 에러 메시지 한국어 통일

### Phase 2 체크리스트
- [ ] `ChatService`에 LRU 기반 메모리 관리 구현
- [ ] 데이터베이스 인덱스 추가
- [ ] 각 서비스별 단위 테스트 작성
- [ ] API 엔드포인트 통합 테스트 작성
- [ ] 큐 시스템 성능 테스트 작성

### Phase 3 체크리스트
- [ ] `requirements.txt` 최적화 (63개 → 45개)
- [ ] 불필요한 문서 파일 삭제
- [ ] 새로운 README.md 작성
- [ ] `docs/SETUP.md` 작성
- [ ] `docs/API.md` 작성
- [ ] `docs/TROUBLESHOOTING.md` 작성