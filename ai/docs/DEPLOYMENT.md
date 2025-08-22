# 🚀 배포 가이드

ALaw AI-Backend의 로컬 및 프로덕션 배포 가이드입니다.

## 📋 목차

- [시스템 요구사항](#시스템-요구사항)
- [로컬 개발 환경](#로컬-개발-환경)
- [Docker 배포](#docker-배포)
- [프로덕션 배포](#프로덕션-배포)
- [CI/CD 파이프라인](#cicd-파이프라인)
- [모니터링](#모니터링)
- [트러블슈팅](#트러블슈팅)

---

## 시스템 요구사항

### 최소 요구사항
- **CPU**: 4 코어 이상
- **메모리**: 8GB RAM 이상
- **디스크**: 50GB 이상 여유 공간
- **Python**: 3.10 이상
- **PostgreSQL**: 12 이상 (pgvector 확장 필요)

### 권장 요구사항
- **CPU**: 8 코어 이상
- **메모리**: 16GB RAM 이상
- **디스크**: 100GB 이상 SSD
- **GPU**: CUDA 지원 GPU (선택사항)

---

## 로컬 개발 환경

### 1. 기본 설정

```bash
# 리포지토리 클론
git clone https://github.com/your-repo/ALaw-AI-Backend.git
cd ALaw-AI-Backend

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements-dev.txt
```

### 2. 환경 설정

```bash
# 환경 파일 생성
cp config/.env.example config/.env

# 환경 변수 편집
# config/.env 파일에서 다음 값들을 설정:
# - OPENAI_API_KEY
# - DATABASE_URL
# - LOG_LEVEL
```

### 3. 데이터베이스 설정

```bash
# PostgreSQL 설치 (Ubuntu)
sudo apt-get install postgresql postgresql-contrib

# pgvector 확장 설치
sudo apt-get install postgresql-12-pgvector

# 데이터베이스 생성
createdb alaw_ai
psql alaw_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 4. 서버 실행

```bash
# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 스크립트 사용
python -m app.main
```

---

## Docker 배포

### 1. Docker Compose로 전체 시스템 실행

```bash
# 데이터베이스 먼저 실행
cd db
docker-compose up -d

# AI 애플리케이션 실행
cd ../docker
docker-compose up -d --build
```

### 2. 개별 컨테이너 실행

```bash
# 애플리케이션 이미지 빌드
docker build -t alaw-ai-backend .

# 컨테이너 실행
docker run -d \
  --name alaw-ai \
  -p 8000:8000 \
  --env-file config/.env \
  alaw-ai-backend
```

### 3. Docker Compose 구성

**docker/docker-compose.yml**:
```yaml
version: '3.8'

services:
  ai-app:
    build: 
      context: ..
      dockerfile: Dockerfile
    ports:
      - "8997:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/alaw_ai
    volumes:
      - ../config:/app/config
      - ../logs:/app/logs
    networks:
      - db_default
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  db_default:
    external: true
```

---

## 프로덕션 배포

### 1. 서버 준비

```bash
# Docker 및 Docker Compose 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 프로덕션 설정

```bash
# 프로덕션 환경 변수 설정
cp config/.env.example config/.env.production

# 프로덕션 설정 편집
nano config/.env.production
```

**주요 프로덕션 설정**:
```env
# 환경
ENVIRONMENT=production
DEBUG=false

# 데이터베이스
DATABASE_URL=postgresql://user:secure_password@localhost:5432/alaw_ai

# 보안
SECRET_KEY=your-super-secret-key

# 로깅
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# 성능
WORKERS=4
MAX_REQUESTS=1000
```

### 3. 프로덕션 배포 실행

```bash
# 프로덕션 배포
docker-compose -f docker-compose.prod.yml up -d --build

# 헬스체크
curl http://localhost:8997/
curl http://localhost:8997/api/queue/health
```

### 4. 리버스 프록시 설정 (Nginx)

**nginx.conf**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8997;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 지원
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

---

## CI/CD 파이프라인

### GitLab CI/CD 설정

**.gitlab-ci.yml**:
```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: "alaw-ai-backend:$CI_COMMIT_SHA"

test:
  stage: test
  script:
    - pip install -r requirements-dev.txt
    - pytest tests/ -v
  only:
    - merge_requests
    - dev-AI

build:
  stage: build
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker tag $DOCKER_IMAGE alaw-ai-backend:latest
  only:
    - dev-AI

deploy:
  stage: deploy
  script:
    - docker-compose -f docker-compose.prod.yml down
    - docker-compose -f docker-compose.prod.yml up -d --build
    - ./scripts/health-check.sh
  environment:
    name: production
    url: http://122.38.210.80:8997
  only:
    - dev-AI
```

### 배포 스크립트

**scripts/deploy.sh**:
```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# 환경 변수 체크
if [ ! -f "config/.env.production" ]; then
    echo "❌ Production environment file not found"
    exit 1
fi

# 이전 컨테이너 정리
echo "🧹 Cleaning up old containers..."
docker-compose -f docker-compose.prod.yml down

# 새 이미지 빌드 및 배포
echo "🔨 Building and deploying new version..."
docker-compose -f docker-compose.prod.yml up -d --build

# 헬스체크
echo "🏥 Running health check..."
./scripts/health-check.sh

echo "✅ Deployment completed successfully!"
```

**scripts/health-check.sh**:
```bash
#!/bin/bash

URL="http://localhost:8997"
MAX_ATTEMPTS=30
ATTEMPT=1

echo "🏥 Starting health check for $URL"

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS"
    
    if curl -f -s "$URL/api/queue/health" > /dev/null; then
        echo "✅ Service is healthy!"
        exit 0
    fi
    
    sleep 10
    ATTEMPT=$((ATTEMPT + 1))
done

echo "❌ Health check failed after $MAX_ATTEMPTS attempts"
exit 1
```

---

## 모니터링

### 1. 로그 모니터링

```bash
# 실시간 로그 확인
docker-compose logs -f ai-app

# 특정 기간 로그
docker-compose logs --since="1h" ai-app

# 에러 로그만 필터링
docker-compose logs ai-app | grep ERROR
```

### 2. 시스템 모니터링

```bash
# 컨테이너 상태 확인
docker ps

# 리소스 사용량 확인
docker stats

# 큐 시스템 상태 확인
curl http://localhost:8997/api/queue/status/json
```

### 3. 성능 모니터링

**monitoring/docker-compose.yml**:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 트러블슈팅

### 일반적인 문제들

#### 1. 메모리 부족
```bash
# 컨테이너 메모리 사용량 확인
docker stats --no-stream

# 메모리 제한 설정
docker run -m 4g alaw-ai-backend
```

#### 2. 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8000

# 다른 포트 사용
docker run -p 8001:8000 alaw-ai-backend
```

#### 3. 데이터베이스 연결 실패
```bash
# 데이터베이스 컨테이너 상태 확인
docker-compose ps

# 연결 테스트
psql -h localhost -U postgres -d alaw_ai -c "SELECT 1;"
```

#### 4. AI 모델 로딩 실패
```bash
# 모델 다운로드 확인
ls -la ~/.cache/huggingface/

# 수동 모델 다운로드
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')"
```

### 로그 분석

**주요 로그 패턴**:
```bash
# 에러 로그 검색
grep "ERROR" logs/app.log

# 성능 이슈 검색
grep "slow\|timeout\|memory" logs/app.log

# API 응답 시간 분석
grep "response_time" logs/app.log | awk '{print $NF}' | sort -n
```

---

## 백업 및 복구

### 데이터베이스 백업

```bash
# 백업 생성
docker exec postgres pg_dump -U postgres alaw_ai > backup_$(date +%Y%m%d).sql

# 백업 복원
docker exec -i postgres psql -U postgres alaw_ai < backup_20240101.sql
```

### 설정 파일 백업

```bash
# 설정 백업
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ logs/

# 복원
tar -xzf config_backup_20240101.tar.gz
```

---

## 📚 관련 문서

- [아키텍처 가이드](ARCHITECTURE.md)
- [API 문서](API.md)
- [운영 가이드](OPERATIONS.md)
- [개발 가이드](DEVELOPMENT.md)