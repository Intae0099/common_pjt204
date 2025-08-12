# 🔧 운영 및 모니터링 가이드

## 📋 목차
- [서비스 상태 확인](#서비스-상태-확인)
- [운영 명령어](#운영-명령어)
- [장애 대응 가이드](#장애-대응-가이드)
- [성능 모니터링](#성능-모니터링)
- [백업 및 복구](#백업-및-복구)

---

## 📊 서비스 상태 확인

### **헬스체크 엔드포인트**
```bash
# 기본 헬스체크
curl http://122.38.210.80:8997/

# API 문서 확인
curl http://122.38.210.80:8997/docs

# 특정 서비스 상태
curl http://122.38.210.80:8997/health
```

### **Docker 컨테이너 상태**
```bash
# 컨테이너 상태 확인
docker-compose ps

# 실시간 로그 모니터링
docker-compose logs -f ai-app

# 리소스 사용량 확인
docker stats ai-app

# 컨테이너 내부 접속
docker exec -it ai-app /bin/bash
```

### **시스템 리소스 모니터링**
```bash
# 메모리 사용량
free -h

# 디스크 사용량
df -h

# CPU 사용률
top

# 포트 사용 확인
netstat -tulpn | grep :8997
```

---

## 🛠️ 운영 명령어

### **서비스 관리**
```bash
# 서비스 재시작
cd docker
docker-compose restart ai-app

# 서비스 중지
docker-compose stop ai-app

# 서비스 시작
docker-compose start ai-app

# 완전 재배포
docker-compose down
docker-compose up -d --build
```

### **로그 관리**
```bash
# 최근 100줄 로그 확인
docker-compose logs --tail=100 ai-app

# 특정 시간 이후 로그 확인
docker-compose logs --since="2024-01-01T10:00:00" ai-app

# 에러 로그만 필터링
docker-compose logs ai-app | grep -i error

# 로그 파일 직접 확인 (호스트)
tail -f ../logs/$(date +%Y-%m-%d).log

# 로그 파일 용량 확인
du -sh ../logs/
```

### **데이터베이스 연결 확인**
```bash
# 네트워크 확인
docker network ls | grep db_default
docker network inspect db_default

# 데이터베이스 컨테이너 상태
cd ../db && docker-compose ps

# 데이터베이스 연결 테스트
docker exec -it postgres_container psql -U alaw_user -d alaw_db -c "\dt"
```

---

## 🚨 장애 대응 가이드

### **일반적인 문제 해결**

#### **1. AI 모델 로딩 실패**
**증상**: 서비스 시작 후 응답하지 않음, 메모리 부족 오류

```bash
# 문제 진단
docker-compose logs ai-app | grep -i "model\|memory\|error"

# 해결 방법
docker-compose restart ai-app

# 메모리 부족 시
sudo sysctl vm.overcommit_memory=1
docker system prune -f
```

#### **2. 데이터베이스 연결 오류**
**증상**: API 요청 시 500 에러, 데이터베이스 연결 실패

```bash
# 문제 진단
cd ../db && docker-compose ps
docker-compose logs db

# 해결 방법
cd ../db && docker-compose restart
docker network inspect db_default
```

#### **3. 포트 충돌**
**증상**: 컨테이너 실행 실패, "port already in use" 오류

```bash
# 문제 진단
netstat -tulpn | grep :8997
lsof -i :8997

# 해결 방법
# 충돌 프로세스 종료
kill -9 [PID]

# 또는 포트 변경
# docker-compose.yml에서 ports: "8998:8000"으로 수정
```

#### **4. 디스크 공간 부족**
**증상**: 로그 파일 생성 실패, Docker 빌드 실패

```bash
# 문제 진단
df -h
du -sh ../logs/
du -sh /var/lib/docker/

# 해결 방법
# 오래된 로그 정리
find ../logs/ -name "*.log" -mtime +7 -delete

# Docker 시스템 정리
docker system prune -a
docker volume prune
```

### **긴급 복구 절차**

#### **1. 전체 서비스 재시작**
```bash
cd docker
docker-compose down
docker-compose up -d --build
```

#### **2. 이전 버전으로 롤백**
```bash
# Git에서 이전 커밋으로 롤백
git log --oneline -10
git checkout [이전_커밋_해시]

# 수동 배포
cd docker
docker-compose down
docker-compose up -d --build
```

#### **3. 데이터 백업 및 복구**
```bash
# 로그 백업
cp -r ../logs ../logs_backup_$(date +%Y%m%d_%H%M%S)

# 데이터 백업
cp -r ../data ../data_backup_$(date +%Y%m%d_%H%M%S)

# 데이터베이스 백업
cd ../db
docker exec postgres_container pg_dump -U alaw_user alaw_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 📈 성능 모니터링

### **리소스 사용량 모니터링**
```bash
# 실시간 컨테이너 리소스 모니터링
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# 시스템 전체 모니터링
htop

# 메모리 상세 분석
cat /proc/meminfo
```

### **성능 지표**
- **메모리 사용량**: AI 모델 로딩 시 ~4GB 사용
- **CPU 사용률**: 추론 시 높은 사용률 (70-90%)
- **디스크 I/O**: 로그 및 데이터 축적으로 지속적 증가
- **네트워크**: HTTP 요청 처리에 따른 네트워크 트래픽

### **성능 임계값 알림**
```bash
# 메모리 사용률 90% 초과 시 알림
while true; do
  MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
  if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
    echo "⚠️ 메모리 사용률 경고: ${MEMORY_USAGE}%"
  fi
  sleep 60
done
```

---

## 💾 백업 및 복구

### **정기 백업 스크립트**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/alaw_ai_$DATE"

mkdir -p $BACKUP_DIR

# 로그 백업
cp -r ../logs $BACKUP_DIR/

# 데이터 백업
cp -r ../data $BACKUP_DIR/

# 설정 파일 백업
cp -r ../config $BACKUP_DIR/

# 데이터베이스 백업
cd ../db
docker exec postgres_container pg_dump -U alaw_user alaw_db > $BACKUP_DIR/database_backup.sql

echo "✅ 백업 완료: $BACKUP_DIR"
```

### **복구 절차**
```bash
# 1. 서비스 중지
cd docker && docker-compose down

# 2. 백업에서 복구
BACKUP_DATE="20240807_143000"
cp -r /backup/alaw_ai_$BACKUP_DATE/logs ../
cp -r /backup/alaw_ai_$BACKUP_DATE/data ../
cp -r /backup/alaw_ai_$BACKUP_DATE/config ../

# 3. 데이터베이스 복구
cd ../db
docker-compose up -d
docker exec postgres_container psql -U alaw_user -d alaw_db < /backup/alaw_ai_$BACKUP_DATE/database_backup.sql

# 4. 서비스 재시작
cd ../docker && docker-compose up -d
```

