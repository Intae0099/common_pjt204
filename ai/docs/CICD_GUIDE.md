# 🚀 CI/CD 및 자동 배포 가이드

## 📋 목차
- [GitLab CI/CD 파이프라인](#gitlab-cicd-파이프라인)
- [배포 프로세스](#배포-프로세스)
- [Mattermost 알림 시스템](#mattermost-알림-시스템)
- [GitLab Runner 설정](#gitlab-runner-설정)
- [환경변수 관리](#환경변수-관리)

---

## 🔄 GitLab CI/CD 파이프라인

### **파이프라인 트리거 조건**
- **브랜치**: `dev-AI` 브랜치로 Push 시 자동 실행
- **실행 환경**: Windows GitLab Runner (Shell Executor)

### **배포 시간**
- **전체 배포**: 약 15-20분 (AI 모델 로딩 포함)
- **Docker 빌드**: 약 5-8분
- **AI 모델 초기화**: 약 3-10분

---

## 🛠️ 배포 프로세스

### **자동화된 배포 단계**

1. **환경 준비**
   - 로컬 `config/.env` 파일 자동 복사
   - 빌드 디렉토리 초기화

2. **Docker 빌드**
   - 최신 코드로 이미지 재빌드
   - 의존성 패키지 설치
   - AI 모델 및 라이브러리 로딩

3. **서비스 배포**
   - 기존 컨테이너 정리 (`docker-compose down`)
   - 새 버전 컨테이너 실행 (`docker-compose up -d --build`)

4. **스마트 헬스체크**
   - AI 모델 로딩 완료까지 최대 10분 대기
   - 30초마다 서비스 상태 확인 (최대 20회 시도)
   - HTTP 요청으로 서비스 준비 상태 검증

5. **배포 결과 알림**
   - Mattermost로 배포 성공/실패 실시간 알림
   - 브랜치, 커밋 정보, 배포 URL 포함

---

## 🔔 Mattermost 알림 시스템

### **성공 알림 예시**
```
✅ AI 애플리케이션 배포 성공!

브랜치: dev-AI
커밋: fc25cf03 - feat: 새 기능 추가
배포 URL: http://122.38.210.80:8997/
파이프라인: [링크]
```

### **실패 알림 예시**
```
❌ AI 애플리케이션 배포 실패!

브랜치: dev-AI
커밋: fc25cf03 - 오류 수정 시도
실패 원인: 파이프라인 실행 중 오류 발생
로그 확인: [링크]
```

---

## 🛠️ GitLab Runner 설정

### **로컬 Runner 설치** (Windows)
```bash
# GitLab Runner 다운로드 및 설치
curl -L --output gitlab-runner.exe "https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-windows-amd64.exe"
gitlab-runner.exe install
gitlab-runner.exe start

# Runner 등록
gitlab-runner.exe register
```

### **Runner 등록 정보**
- **GitLab URL**: `https://lab.ssafy.com/`
- **Description**: `Windows AI Server Runner`
- **Executor**: `shell`
- **작업 디렉토리**: `F:\S13P11B204\ai\builds`
- **캐시 디렉토리**: `F:\S13P11B204\ai\cache`

---

## 🔐 환경변수 관리

### **GitLab CI/CD Variables**
프로젝트에서 사용하는 보안 환경변수:

| Variable | Description | Required |
|----------|-------------|----------|
| `MATTERMOST_WEBHOOK_URL` | 팀 알림용 Mattermost 웹훅 URL | ✅ |

**설정 위치**: `GitLab Project → Settings → CI/CD → Variables`

### **로컬 환경변수** (`config/.env`)
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Database
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=alaw_db

# External APIs
GMS_KEY=your_gms_api_key

# Server Configuration
CORS_ORIGINS=http://localhost:5173,http://122.38.210.80:3000
```

---

## 🔧 GitLab CI 파일 구조

### **`.gitlab-ci.yml` 주요 구성**
```yaml
stages:
  - deploy

deploy:
  stage: deploy
  before_script:
    - # 환경 준비 및 파일 복사
  script:
    - # Docker 빌드 및 배포
    - # 스마트 헬스체크
  after_script:
    - # Mattermost 알림 전송
  only:
    - dev-AI
```

### **PowerShell 스크립트 최적화**
- Windows 환경에 최적화된 PowerShell 명령어 사용
- 오류 처리 및 재시도 로직 구현
- 실시간 진행 상황 표시

---

## 🚨 문제 해결

### **일반적인 CI/CD 문제**

1. **Runner 연결 실패**
   ```bash
   # Runner 상태 확인
   gitlab-runner.exe status
   
   # Runner 재시작
   gitlab-runner.exe restart
   ```

2. **환경변수 파일 없음**
   - 로컬 `config/.env` 파일 존재 확인
   - GitLab Variables 설정 확인

3. **Docker 빌드 실패**
   ```bash
   # Docker 상태 확인
   docker --version
   docker-compose --version
   
   # 수동 빌드 테스트
   cd docker
   docker-compose up --build
   ```

4. **헬스체크 타임아웃**
   - AI 모델 로딩 시간이 10분 초과하는 경우
   - 서버 리소스 부족 시 발생
   - 메모리 확인 및 불필요한 프로세스 종료

---

## 📊 배포 모니터링

### **파이프라인 모니터링**
- **GitLab UI**: Pipelines 페이지에서 실시간 진행 상황 확인
- **Mattermost 알림**: 배포 완료 즉시 팀 채널 알림
- **로그 확인**: 각 단계별 상세 로그 제공

### **성능 지표**
- **성공률**: 95% 이상 배포 성공률 유지
- **배포 시간**: 평균 18분 (AI 모델 로딩 포함)
- **롤백 시간**: 필요시 5분 내 이전 버전 복구 가능