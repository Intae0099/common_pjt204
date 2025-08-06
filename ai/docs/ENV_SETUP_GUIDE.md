# 환경설정 가이드

## 빠른 시작

1. **환경설정 파일 생성**:
```bash
cp config/.env.example config/.env
```

2. **필수 환경변수 설정** (`.env` 파일에서):

### 🔴 필수 설정 (반드시 설정해야 함)
```bash
# LLM API 키
GMS_KEY=your_actual_api_key_here

# 데이터베이스 연결 정보
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_NAME=legal_ai_db
```

### 🟡 권장 설정 (기본값이 있지만 확인 필요)
```bash
# API 서버 포트 (다른 서비스와 충돌 시 변경)
API_PORT=8000

# CORS 도메인 (프론트엔드 주소)
CORS_ORIGINS=http://localhost:5173,https://i13b204.p.ssafy.io
```

### 🟢 선택적 설정 (기본값으로도 동작)
모든 기타 설정들은 합리적인 기본값을 가지고 있습니다.

## 환경변수 우선순위

1. 시스템 환경변수
2. `.env` 파일의 값
3. 코드에서 정의한 기본값

## 로컬 개발 환경 예시

```bash
# 🤖 AI 모델
GMS_KEY=sk-proj-abcd1234...
LLM_MAX_RETRIES=3
MAX_HISTORY_TOKENS=3000

# 🗄️ 데이터베이스 (로컬 PostgreSQL)
DB_USER=postgres
DB_PASSWORD=1234
DB_HOST=localhost
DB_PORT=5432
DB_NAME=legal_ai_db

# 🌐 API 서버
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
CORS_ORIGINS=http://localhost:5173

# 📝 로깅
LOG_LEVEL=DEBUG

# 로그 출력 예시:
# [2025-08-06 11:45:23][INFO][StructuringService] 사건 구조화 시작  
# [2025-08-06 11:45:23][INFO][StructuringService] 사건 구조화 완료 [245ms]
```

## Docker 개발 환경 예시

```bash
# 🤖 AI 모델 (동일)
GMS_KEY=sk-proj-abcd1234...

# 🗄️ 데이터베이스 (Docker 컨테이너)
DB_USER=postgres
DB_PASSWORD=1234
DB_HOST=db  # Docker Compose 서비스명
DB_PORT=5432
DB_NAME=legal_ai_db

# 기타는 동일...
```

## 프로덕션 환경 예시

```bash
# 🤖 AI 모델
GMS_KEY=sk-proj-production-key...
LLM_MAX_RETRIES=5
MAX_HISTORY_TOKENS=2000

# 🗄️ 데이터베이스 (원격)
DB_USER=app_user
DB_PASSWORD=super_secure_password
DB_HOST=db.yourdomain.com
DB_PORT=5432
DB_NAME=legal_ai_production

# 🌐 API 서버
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 📝 로깅
LOG_LEVEL=WARNING
LOG_FILE_PATH=/var/log/legal-ai/app.log
```

## 문제 해결

### 설정 파일을 읽을 수 없는 경우
- `.env` 파일이 `config/` 디렉토리에 있는지 확인
- 파일 권한 확인 (`chmod 600 config/.env`)

### 데이터베이스 연결 오류
- PostgreSQL 서버가 실행 중인지 확인
- DB 계정/비밀번호가 정확한지 확인
- pgvector 확장이 설치되어 있는지 확인

### API 키 관련 오류
- GMS_KEY가 올바르게 설정되었는지 확인
- 키에 특수문자가 포함된 경우 따옴표로 감싸기

## 보안 주의사항

- ⚠️ **절대로 `.env` 파일을 Git에 커밋하지 마세요**
- 🔒 프로덕션 환경에서는 환경변수를 시스템 레벨에서 설정하는 것을 권장
- 🛡️ API 키와 비밀번호는 정기적으로 교체
- 📝 `.env` 파일 권한을 600 (소유자만 읽기/쓰기)으로 설정