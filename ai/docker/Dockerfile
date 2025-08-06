# Python 3.11 base image
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 종속성 설치
COPY requirements.txt .

# 기본 패키지 먼저 설치
RUN pip install --no-cache-dir --upgrade pip

# PyTorch 먼저 설치 (CPU 버전)
RUN pip install --no-cache-dir torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu

# 나머지 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 애플리케이션 시작
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]