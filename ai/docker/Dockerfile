# CUDA 12.8 지원 PyTorch 공식 베이스 이미지 사용
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-devel

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgomp1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 기본 패키지 먼저 설치
RUN pip install --no-cache-dir --upgrade pip

# CUDA 환경 변수 설정
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV CUDA_DEVICE_ORDER=PCI_BUS_ID

# PyTorch CUDA 지원 확인 (이미 설치되어 있지만 확인)
RUN python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'cuDNN version: {torch.backends.cudnn.version()}')"

# 로컬 파일 복사 (GitLab Runner에서 이미 최신 코드 보유)
COPY config/.env config/.env
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# GPU 메모리 체크를 위한 추가 검증
RUN python -c "import torch; print(f'GPU device count: {torch.cuda.device_count()}'); [print(f'GPU {i}: {torch.cuda.get_device_name(i)}') for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else print('No GPU detected')"

# 애플리케이션 코드 복사
COPY . /app/

# 포트 노출
EXPOSE 8000

# 애플리케이션 시작
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]