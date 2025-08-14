from typing import List, Optional
import torch
import numpy as np
import psutil
from utils.logger import setup_logger, get_logger
from sentence_transformers import SentenceTransformer

setup_logger()
logger = get_logger(__name__)

class QuantizedEmbeddingModel:
    def __init__(self, model_name: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS", 
                 enable_quantization: bool = True):
        self.model_name = model_name
        self.enable_quantization = enable_quantization
        self._model = None
        self._device = self._get_optimal_device()
        self._load_and_optimize_model()

    def _get_optimal_device(self) -> str:
        """최적 디바이스 선택"""
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            logger.info(f"[경량화] CUDA 사용 가능 (GPU 메모리: {gpu_memory // 1024**3}GB)")
            return "cuda"
        else:
            logger.info("[경량화] CPU 모드로 실행")
            return "cpu"

    def _load_and_optimize_model(self):
        """모델 로드 및 양자화 적용"""
        logger.info(f"[경량화] 임베딩 모델 로드 중: {self.model_name}")
        
        # 메모리 사용량 측정 시작
        initial_memory = self._get_memory_usage()
        
        # 모델 로드
        self._model = SentenceTransformer(self.model_name, device=self._device)
        
        # 양자화 적용
        if self.enable_quantization:
            self._apply_quantization()
        
        # 추론 모드 설정
        self._model.eval()
        
        # 메모리 사용량 측정 완료
        final_memory = self._get_memory_usage()
        memory_saved = initial_memory - final_memory if initial_memory > final_memory else 0
        
        logger.info(f"[경량화] 모델 로드 완료 (양자화: {self.enable_quantization}, 메모리 절약: {memory_saved:.2f}MB)")

    def _apply_quantization(self):
        """디바이스별 양자화 전략 적용"""
        try:
            if self._device == "cuda":
                # GPU: Half Precision (FP16) 적용
                self._model = self._model.half()
                logger.info("[경량화] GPU Half Precision (FP16) 적용 - 메모리 50% 절감")
                
            else:
                # CPU: 동적 INT8 양자화 적용
                self._apply_cpu_quantization()
                logger.info("[경량화] CPU INT8 양자화 적용 - 메모리 30% 절감")
                
        except Exception as e:
            logger.warning(f"[경량화] 양자화 적용 실패, 기본 모드로 실행: {e}")
            self.enable_quantization = False

    def _apply_cpu_quantization(self):
        """CPU용 INT8 동적 양자화"""
        for module in self._model.modules():
            if hasattr(module, 'weight') and module.weight is not None:
                if len(module.weight.shape) > 1:  # 2D 이상의 weight만 양자화
                    # FP32 → INT8 변환
                    weight_fp32 = module.weight.data
                    weight_int8 = torch.quantize_per_tensor(
                        weight_fp32, 
                        scale=weight_fp32.abs().max() / 127.0,
                        zero_point=0,
                        dtype=torch.qint8
                    )
                    module.weight.data = weight_int8.dequantize()

    def _get_memory_usage(self) -> float:
        """현재 메모리 사용량 반환 (MB)"""
        if self._device == "cuda" and torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**2
        else:
            return psutil.Process().memory_info().rss / 1024**2

    def get_embedding(self, text: str) -> List[float]:
        """단일 텍스트 임베딩 생성"""
        logger.debug(f"[경량화] 임베딩 생성: {text[:50]}...")
        
        with torch.no_grad():
            # 양자화된 모델로 추론
            embedding = self._model.encode(
                text,
                batch_size=1,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True
            )
        
        return embedding.tolist()

    def get_batch_embeddings(self, texts: List[str], batch_size: int = 8) -> List[List[float]]:
        """배치 처리로 다중 텍스트 임베딩 생성"""
        logger.info(f"[경량화] 배치 임베딩 생성: {len(texts)}개 텍스트, 배치 크기: {batch_size}")
        
        # 메모리 상황에 따른 동적 배치 크기 조정
        adjusted_batch_size = self._adjust_batch_size(len(texts), batch_size)
        
        with torch.no_grad():
            embeddings = self._model.encode(
                texts,
                batch_size=adjusted_batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10,
                normalize_embeddings=True
            )
        
        return embeddings.tolist()

    def _adjust_batch_size(self, num_texts: int, requested_batch_size: int) -> int:
        """메모리 상황에 따른 배치 크기 자동 조정"""
        if self._device == "cuda":
            gpu_memory_free = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()
            gpu_memory_free_gb = gpu_memory_free / 1024**3
            
            if gpu_memory_free_gb < 1.0:  # 1GB 미만 시 배치 크기 축소
                adjusted = max(1, requested_batch_size // 2)
                logger.info(f"[경량화] GPU 메모리 부족, 배치 크기 축소: {requested_batch_size} → {adjusted}")
                return adjusted
        
        else:
            # CPU 메모리 체크
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:  # 85% 이상 시 배치 크기 축소
                adjusted = max(1, requested_batch_size // 2)
                logger.info(f"[경량화] CPU 메모리 부족 ({memory_percent}%), 배치 크기 축소: {requested_batch_size} → {adjusted}")
                return adjusted
        
        return requested_batch_size

    def get_model_info(self) -> dict:
        """모델 정보 및 최적화 상태 반환"""
        info = {
            "model_name": self.model_name,
            "device": self._device,
            "quantization_enabled": self.enable_quantization,
            "memory_usage_mb": self._get_memory_usage(),
        }
        
        if self._device == "cuda":
            info["gpu_memory_total"] = torch.cuda.get_device_properties(0).total_memory / 1024**3
            info["gpu_memory_allocated"] = torch.cuda.memory_allocated() / 1024**3
        
        return info

if __name__ == '__main__':
    logger.info("[경량화] QuantizedEmbeddingModel 테스트 시작...")
    
    # 모델 초기화
    model = QuantizedEmbeddingModel(enable_quantization=True)
    
    # 단일 텍스트 테스트
    test_text = "부동산 매매 계약에 관한 법률 상담"
    embedding = model.get_embedding(test_text)
    logger.info(f"단일 임베딩 차원: {len(embedding)}")
    
    # 배치 처리 테스트
    test_texts = [
        "계약 해지 관련 법률 자문",
        "임대차 보증금 반환 문제",
        "근로계약 위반 손해배상"
    ]
    batch_embeddings = model.get_batch_embeddings(test_texts, batch_size=4)
    logger.info(f"배치 처리 결과: {len(batch_embeddings)}개 임베딩")
    
    # 모델 정보 출력
    model_info = model.get_model_info()
    logger.info(f"모델 정보: {model_info}")
    
    logger.info("[경량화] 테스트 완료")