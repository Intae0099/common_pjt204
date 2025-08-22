# 📊 운영 가이드

ALaw AI-Backend의 프로덕션 운영 및 모니터링 가이드입니다.

## 📋 목차

- [시스템 모니터링](#시스템-모니터링)
- [로그 관리](#로그-관리)
- [성능 최적화](#성능-최적화)
- [장애 대응](#장애-대응)
- [백업 및 복구](#백업-및-복구)
- [보안 관리](#보안-관리)
- [용량 계획](#용량-계획)

---

## 시스템 모니터링

### 1. 헬스체크 엔드포인트

#### 기본 헬스체크
```bash
# 애플리케이션 상태 확인
curl http://localhost:8997/

# 큐 시스템 헬스체크
curl http://localhost:8997/api/queue/health

# 상세 큐 상태 (JSON)
curl http://localhost:8997/api/queue/status/json
```

#### 응답 예시
```json
{
    "status": "healthy",
    "is_running": true,
    "queue_stats": {
        "search": {"pending": 0, "processing": 1, "completed": 15},
        "analysis": {"pending": 2, "processing": 1, "completed": 8}
    },
    "resource_usage": {
        "memory_percent": 68.5,
        "cpu_percent": 35.2
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 시스템 리소스 모니터링

#### CPU 및 메모리 모니터링
```bash
# Docker 컨테이너 리소스 사용량
docker stats alaw-ai-backend

# 시스템 전체 리소스
htop

# 특정 프로세스 모니터링
ps aux | grep python
```

#### 디스크 사용량
```bash
# 디스크 사용량 확인
df -h

# 로그 파일 크기 확인
du -sh logs/
find logs/ -name "*.log" -size +100M

# 데이터베이스 크기 확인
docker exec postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('alaw_ai'));"
```

### 3. 애플리케이션 메트릭

#### 성능 메트릭 수집
```python
# metrics.py
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge

# 요청 카운터
REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])

# 응답 시간 히스토그램
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration')

# 리소스 게이지
MEMORY_USAGE = Gauge('app_memory_usage_bytes', 'Memory usage')
CPU_USAGE = Gauge('app_cpu_usage_percent', 'CPU usage')

def update_system_metrics():
    """시스템 메트릭 업데이트"""
    process = psutil.Process()
    MEMORY_USAGE.set(process.memory_info().rss)
    CPU_USAGE.set(process.cpu_percent())
```

### 4. 알림 설정

#### Mattermost 알림 (기존)
```bash
# 장애 알림 스크립트
#!/bin/bash
# alert.sh

WEBHOOK_URL="your-mattermost-webhook-url"
SERVICE_URL="http://localhost:8997"

if ! curl -f -s "$SERVICE_URL/api/queue/health" > /dev/null; then
    curl -X POST "$WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d '{
            "text": "🚨 ALaw AI-Backend 서비스 장애 감지",
            "channel": "alerts",
            "username": "monitoring-bot"
        }'
fi
```

#### 이메일 알림
```python
# email_alert.py
import smtplib
from email.mime.text import MIMEText

def send_alert_email(subject: str, message: str):
    """알림 이메일 발송"""
    msg = MIMEText(message)
    msg['Subject'] = f"[ALaw AI] {subject}"
    msg['From'] = "alerts@alaw.ai"
    msg['To'] = "admin@alaw.ai"
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("alerts@alaw.ai", "app_password")
    server.send_message(msg)
    server.quit()

# 사용 예시
def check_and_alert():
    try:
        response = requests.get("http://localhost:8997/api/queue/health")
        if response.status_code != 200:
            send_alert_email(
                "서비스 장애",
                f"헬스체크 실패: HTTP {response.status_code}"
            )
    except Exception as e:
        send_alert_email("서비스 장애", f"헬스체크 오류: {str(e)}")
```

---

## 로그 관리

### 1. 로그 구조

```
logs/
├── app.log              # 메인 애플리케이션 로그
├── access.log           # HTTP 요청 로그
├── error.log            # 에러 전용 로그
├── performance.log      # 성능 관련 로그
└── archive/             # 아카이브된 로그
    ├── app.log.2024-01-01.gz
    └── app.log.2024-01-02.gz
```

### 2. 로그 레벨 관리

#### 프로덕션 로그 설정
```python
# config/logging.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 5,
            'formatter': 'detailed'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/error.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
            'level': 'ERROR'
        }
    },
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['file', 'error_file']
        }
    }
}
```

### 3. 로그 분석

#### 자주 사용하는 로그 분석 명령어
```bash
# 에러 로그 확인
grep "ERROR" logs/app.log | tail -20

# 특정 시간대 로그 필터링
grep "2024-01-01 12:" logs/app.log

# API 응답 시간 분석
grep "response_time" logs/app.log | awk '{print $NF}' | sort -n | tail -10

# 가장 빈번한 에러 TOP 10
grep "ERROR" logs/app.log | cut -d':' -f4- | sort | uniq -c | sort -nr | head -10

# 시간당 요청 수 분석
grep "POST\|GET" logs/access.log | cut -d' ' -f1 | cut -d':' -f1-2 | uniq -c
```

#### 로그 분석 스크립트
```python
# log_analyzer.py
import re
import json
from datetime import datetime, timedelta

def analyze_error_patterns(log_file: str, hours: int = 24) -> dict:
    """지난 N시간 동안의 에러 패턴 분석"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    error_patterns = {}
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'ERROR' in line:
                # 타임스탬프 파싱
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                    if timestamp >= cutoff_time:
                        # 에러 메시지 추출
                        error_msg = line.split('ERROR')[-1].strip()
                        error_patterns[error_msg] = error_patterns.get(error_msg, 0) + 1
    
    return dict(sorted(error_patterns.items(), key=lambda x: x[1], reverse=True))

def generate_log_report():
    """로그 분석 리포트 생성"""
    errors = analyze_error_patterns('logs/error.log')
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'top_errors': list(errors.items())[:10],
        'total_errors': sum(errors.values()),
        'unique_errors': len(errors)
    }
    
    return report
```

### 4. 로그 로테이션

#### logrotate 설정
```bash
# /etc/logrotate.d/alaw-ai
/path/to/alaw-ai/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 app app
    postrotate
        docker exec alaw-ai-backend kill -HUP 1
    endscript
}
```

---

## 성능 최적화

### 1. 응답 시간 최적화

#### 데이터베이스 쿼리 최적화
```sql
-- 인덱스 사용률 확인
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_tup_read DESC;

-- 느린 쿼리 식별
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### 애플리케이션 성능 프로파일링
```python
# profiling.py
import cProfile
import pstats
from functools import wraps

def profile_function(func):
    """함수 실행 프로파일링"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(10)  # 상위 10개 함수
    
    return wrapper

# 사용 예시
@profile_function
async def slow_function():
    # 분석할 함수
    pass
```

### 2. 메모리 최적화

#### 메모리 사용량 모니터링
```python
# memory_monitor.py
import psutil
import gc
from memory_profiler import profile

@profile
def memory_intensive_function():
    """메모리 집약적 함수 분석"""
    # 메모리 사용량 분석할 코드
    pass

def check_memory_leaks():
    """메모리 누수 체크"""
    gc.collect()
    memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    if memory_usage > 1000:  # 1GB 초과 시 알림
        logger.warning(f"높은 메모리 사용량 감지: {memory_usage:.2f}MB")
        
        # 가비지 컬렉션 상태 확인
        logger.info(f"GC 카운트: {gc.get_count()}")
        logger.info(f"GC 통계: {gc.get_stats()}")
```

### 3. 큐 시스템 최적화

#### 큐 성능 튜닝
```python
# queue_tuning.py
OPTIMIZED_LIMITS = {
    "search": {
        "max_concurrent": 3,  # 기본값: 2
        "max_queue_size": 20,  # 기본값: 10
        "timeout": 60  # 기본값: 30
    },
    "case_analysis": {
        "max_concurrent": 2,  # 기본값: 1
        "max_queue_size": 15,  # 기본값: 5
        "timeout": 120  # 기본값: 60
    }
}

def optimize_queue_settings():
    """리소스 상황에 따른 큐 설정 최적화"""
    memory_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent(interval=1)
    
    if memory_percent < 60 and cpu_percent < 50:
        # 리소스 여유 있을 때 동시 처리 증가
        return OPTIMIZED_LIMITS
    else:
        # 리소스 부족 시 보수적 설정
        return CONSERVATIVE_LIMITS
```

---

## 장애 대응

### 1. 일반적인 장애 시나리오

#### 서비스 응답 없음
```bash
# 1. 프로세스 상태 확인
docker ps | grep alaw-ai
docker logs alaw-ai-backend --tail=50

# 2. 리소스 사용량 확인
docker stats alaw-ai-backend

# 3. 헬스체크 직접 실행
curl -v http://localhost:8997/api/queue/health

# 4. 컨테이너 재시작
docker restart alaw-ai-backend

# 5. 완전 재배포 (필요시)
cd docker && docker-compose down && docker-compose up -d --build
```

#### 데이터베이스 연결 실패
```bash
# 1. PostgreSQL 상태 확인
docker exec postgres pg_isready

# 2. 연결 테스트
docker exec postgres psql -U postgres -c "SELECT 1;"

# 3. 연결 수 확인
docker exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 4. 데이터베이스 재시작 (필요시)
cd db && docker-compose restart postgres
```

#### 큐 시스템 정체
```bash
# 1. 큐 상태 확인
curl http://localhost:8997/api/queue/status/json

# 2. 정체된 작업 확인
sqlite3 data/queue.db "SELECT * FROM tasks WHERE status='processing' ORDER BY created_at;"

# 3. 큐 정리 (신중히 실행)
curl -X POST http://localhost:8997/api/queue/clear

# 4. 서비스 재시작
docker restart alaw-ai-backend
```

### 2. 자동 복구 스크립트

```bash
#!/bin/bash
# auto_recovery.sh

LOG_FILE="/var/log/alaw-ai-recovery.log"
SERVICE_URL="http://localhost:8997"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

check_and_recover() {
    log_message "헬스체크 시작"
    
    # 헬스체크 실행
    if curl -f -s "$SERVICE_URL/api/queue/health" > /dev/null; then
        log_message "서비스 정상"
        return 0
    fi
    
    log_message "서비스 장애 감지, 복구 시작"
    
    # 1차 시도: 컨테이너 재시작
    docker restart alaw-ai-backend
    sleep 30
    
    if curl -f -s "$SERVICE_URL/api/queue/health" > /dev/null; then
        log_message "컨테이너 재시작으로 복구 완료"
        return 0
    fi
    
    # 2차 시도: 완전 재배포
    cd /path/to/docker
    docker-compose down
    docker-compose up -d --build
    sleep 60
    
    if curl -f -s "$SERVICE_URL/api/queue/health" > /dev/null; then
        log_message "완전 재배포로 복구 완료"
        return 0
    fi
    
    log_message "자동 복구 실패, 수동 개입 필요"
    # 알림 발송
    send_alert_notification "자동 복구 실패"
    
    return 1
}

# 매 5분마다 실행하도록 crontab 설정
# */5 * * * * /path/to/auto_recovery.sh
```

### 3. 장애 에스컬레이션

#### 1단계: 자동 복구
- 헬스체크 실패 시 자동 재시작
- 큐 정체 시 자동 정리
- 임시 파일 정리

#### 2단계: 개발팀 알림
- Mattermost/Slack 알림
- 이메일 알림
- SMS 알림 (중요 장애)

#### 3단계: 수동 개입
- 로그 분석
- 데이터베이스 상태 확인
- 인프라 점검

---

## 백업 및 복구

### 1. 데이터베이스 백업

#### 자동 백업 스크립트
```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="alaw_ai"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 데이터베이스 덤프
docker exec postgres pg_dump -U postgres "$DB_NAME" | gzip > "$BACKUP_DIR/backup_${DATE}.sql.gz"

# 오래된 백업 파일 정리 (30일 이상)
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +30 -delete

echo "백업 완료: backup_${DATE}.sql.gz"
```

#### 복구 스크립트
```bash
#!/bin/bash
# restore_db.sh

BACKUP_FILE="$1"
DB_NAME="alaw_ai"

if [ -z "$BACKUP_FILE" ]; then
    echo "사용법: $0 <백업파일경로>"
    exit 1
fi

# 기존 데이터베이스 삭제 및 재생성 (주의!)
docker exec postgres dropdb -U postgres "$DB_NAME"
docker exec postgres createdb -U postgres "$DB_NAME"

# 백업 복원
gunzip -c "$BACKUP_FILE" | docker exec -i postgres psql -U postgres "$DB_NAME"

echo "복구 완료"
```

### 2. 설정 파일 백업

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# 설정 파일들 백업
tar -czf "$BACKUP_DIR/config_${DATE}.tar.gz" \
    config/ \
    docker/ \
    logs/ \
    --exclude="logs/*.log" \
    --exclude="*.pyc"

echo "설정 백업 완료: config_${DATE}.tar.gz"
```

### 3. BM25 검색 캐시 관리

- **캐시 파일**: `data/preprocessed/bm25_cache.pkl`
- **역할**: BM25 검색 모델을 저장하여 서버 시작 시간을 단축시키는 역할을 합니다.
- **운영 가이드**:
  - **백업**: 이 파일은 원본 데이터로부터 재생성 가능하므로, 필수 백업 대상은 아닙니다. 하지만 용량이 크고 생성에 수 분이 걸리므로, 서버 이전 등 빠른 복구가 필요할 경우 함께 백업하는 것을 권장합니다.
  - **갱신**: 새로운 판례 데이터가 `data/preprocessed`에 추가되어 검색 모델을 갱신해야 할 경우, 이 캐시 파일을 삭제 후 서버를 재시작하면 자동으로 재생성됩니다.

### 3. 크론 작업 설정
```

```bash
# crontab -e
# 매일 오전 2시 데이터베이스 백업
0 2 * * * /path/to/backup_db.sh

# 매주 일요일 오전 3시 설정 백업
0 3 * * 0 /path/to/backup_config.sh

# 매 5분마다 헬스체크 및 자동 복구
*/5 * * * * /path/to/auto_recovery.sh
```

---

## 보안 관리

### 1. 접근 제어

#### 방화벽 설정
```bash
# UFW 설정 (Ubuntu)
sudo ufw allow 22          # SSH
sudo ufw allow 8997        # 애플리케이션
sudo ufw allow 5432/tcp    # PostgreSQL (필요시)
sudo ufw enable
```

#### Nginx 프록시 보안
```nginx
# /etc/nginx/sites-available/alaw-ai
server {
    listen 80;
    server_name alaw-ai.example.com;
    
    # 보안 헤더
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:8997;
        
        # 클라이언트 IP 전달
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2. 보안 모니터링

#### 접근 로그 분석
```bash
# 의심스러운 접근 패턴 탐지
tail -f /var/log/nginx/access.log | grep -E "(POST|PUT|DELETE)" | grep -v "200\|201"

# IP별 요청 빈도 분석
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -20

# 실패한 로그인 시도 감지
grep "401\|403" /var/log/nginx/access.log | tail -20
```

### 3. 민감 정보 보호

#### 환경 변수 암호화
```bash
# 민감한 환경 변수는 암호화하여 저장
echo "sensitive_value" | gpg --symmetric --armor > .env.encrypted

# 실행 시 복호화
gpg --decrypt .env.encrypted > .env.tmp
source .env.tmp
rm .env.tmp
```

---

## 용량 계획

### 1. 리소스 사용량 예측

#### 동시 사용자 기준 용량 계획
```python
# capacity_planning.py
def calculate_resources(concurrent_users: int) -> dict:
    """동시 사용자 수 기반 리소스 계산"""
    
    # 사용자당 평균 리소스 사용량
    cpu_per_user = 0.1  # CPU 코어
    memory_per_user = 50  # MB
    
    # 기본 시스템 오버헤드
    base_cpu = 2
    base_memory = 2048  # MB
    
    total_cpu = base_cpu + (concurrent_users * cpu_per_user)
    total_memory = base_memory + (concurrent_users * memory_per_user)
    
    return {
        "concurrent_users": concurrent_users,
        "required_cpu_cores": round(total_cpu, 1),
        "required_memory_mb": int(total_memory),
        "recommended_cpu_cores": round(total_cpu * 1.5, 1),  # 50% 여유
        "recommended_memory_mb": int(total_memory * 1.3)      # 30% 여유
    }

# 예측 결과
for users in [10, 50, 100, 200]:
    resources = calculate_resources(users)
    print(f"동시 사용자 {users}명: CPU {resources['recommended_cpu_cores']}코어, "
          f"메모리 {resources['recommended_memory_mb']}MB")
```

### 2. 확장 계획

#### 수직 확장 (Scale Up)
```yaml
# docker-compose.scale-up.yml
version: '3.8'
services:
  ai-app:
    deploy:
      resources:
        limits:
          cpus: '8.0'
          memory: 16G
        reservations:
          cpus: '4.0'
          memory: 8G
```

#### 수평 확장 (Scale Out)
```yaml
# docker-compose.scale-out.yml
version: '3.8'
services:
  ai-app:
    scale: 3  # 3개 인스턴스 실행
    environment:
      - INSTANCE_ID=${HOSTNAME}
  
  load-balancer:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

---

## 📚 관련 문서

- [배포 가이드](DEPLOYMENT.md)
- [아키텍처 가이드](ARCHITECTURE.md)
- [API 문서](API.md)
- [개발 가이드](DEVELOPMENT.md)