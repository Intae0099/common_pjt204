# Docker 배포 가이드

## 환경변수 설정

### 로컬 개발용
```bash
# 필수 환경변수 설정
export DB_PASSWORD="your_secure_db_password"
export GMS_KEY="your_gms_api_key"

# 선택적 환경변수 (기본값 사용 가능)
export CORS_ORIGINS="http://localhost:5173,https://your-domain.com"
```

### CI/CD용 GitHub Secrets
GitHub Repository → Settings → Secrets and variables → Actions에서 설정:
- `DB_PASSWORD`: 데이터베이스 비밀번호
- `GMS_KEY`: GMS API 키
- `CORS_ORIGINS`: CORS 허용 도메인 (선택사항)

## 사용 방법

### 1. 로컬 실행
```bash
cd docker
docker-compose up -d
```

### 2. 서비스 확인
```bash
# AI 앱 상태 확인
curl http://localhost:8000/

# 로그 확인
docker-compose logs ai-app
```

### 3. 서비스 중지
```bash
docker-compose down
```

## 보안 주의사항
- 환경변수 파일(.env)을 Git에 커밋하지 마세요
- 운영 환경에서는 강력한 패스워드 사용
- API 키는 절대 코드에 하드코딩하지 마세요