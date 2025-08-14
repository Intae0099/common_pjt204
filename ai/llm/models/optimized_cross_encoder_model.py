from sentence_transformers import CrossEncoder
from typing import List, Tuple
import torch
import numpy as np
import psutil
import time
from utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

class OptimizedCrossEncoderModel:
    def __init__(self, model_name: str = "Alibaba-NLP/gte-multilingual-base", 
                 enable_quantization: bool = True, max_batch_size: int = 16):
        self.model_name = model_name
        self.enable_quantization = enable_quantization
        self.max_batch_size = max_batch_size
        self._model = None
        self._device = self._get_optimal_device()
        self._load_and_optimize_model()

    def _get_optimal_device(self) -> str:
        """최적 디바이스 선택"""
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            logger.info(f"[경량화] Cross-encoder CUDA 사용 (GPU 메모리: {gpu_memory // 1024**3}GB)")
            return "cuda"
        else:
            logger.info("[경량화] Cross-encoder CPU 모드로 실행")
            return "cpu"

    def _load_and_optimize_model(self):
        """모델 로드 및 최적화 적용"""
        logger.info(f"[경량화] Cross-encoder 모델 로드 중: {self.model_name}")
        
        # 메모리 사용량 측정 시작
        initial_memory = self._get_memory_usage()
        
        # 모델 로드
        self._model = CrossEncoder(
            model_name_or_path=self.model_name,
            device=self._device,
            trust_remote_code=True
        )
        
        # 양자화 적용
        if self.enable_quantization:
            self._apply_quantization()
        
        # 추론 모드 설정
        self._model.model.eval()
        
        # 메모리 사용량 측정 완료
        final_memory = self._get_memory_usage()
        memory_saved = initial_memory - final_memory if initial_memory > final_memory else 0
        
        logger.info(f"[경량화] Cross-encoder 로드 완료 (양자화: {self.enable_quantization}, 메모리 절약: {memory_saved:.2f}MB)")

    def _apply_quantization(self):
        """디바이스별 양자화 전략 적용"""
        try:
            if self._device == "cuda":
                # GPU: Half Precision (FP16) 적용
                self._model.model = self._model.model.half()
                logger.info("[경량화] Cross-encoder GPU Half Precision (FP16) 적용 - 메모리 50% 절감")
                
            else:
                # CPU: 동적 양자화 적용
                self._apply_cpu_quantization()
                logger.info("[경량화] Cross-encoder CPU 동적 양자화 적용 - 메모리 30% 절감")
                
        except Exception as e:
            logger.warning(f"[경량화] Cross-encoder 양자화 적용 실패, 기본 모드로 실행: {e}")
            self.enable_quantization = False

    def _apply_cpu_quantization(self):
        """CPU용 동적 양자화"""
        # PyTorch 동적 양자화 적용
        self._model.model = torch.quantization.quantize_dynamic(
            self._model.model,
            {torch.nn.Linear},  # Linear 레이어만 양자화
            dtype=torch.qint8
        )

    def _get_memory_usage(self) -> float:
        """현재 메모리 사용량 반환 (MB)"""
        if self._device == "cuda" and torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**2
        else:
            return psutil.Process().memory_info().rss / 1024**2

    def get_cross_encoder_scores(self, query: str, documents: List[str]) -> List[float]:
        """배치 최적화된 Cross-encoder 점수 계산"""
        if not documents:
            return []

        logger.debug(f"[경량화] Cross-encoder 점수 계산: {len(documents)}개 문서")
        
        # 메모리와 처리량을 고려한 최적 배치 크기 결정
        optimal_batch_size = self._get_optimal_batch_size(len(documents))
        
        # 문서-쿼리 쌍 생성
        sentence_pairs = [[query, doc] for doc in documents]
        
        # 배치 처리
        all_scores = []
        start_time = time.time()
        
        with torch.no_grad():
            for i in range(0, len(sentence_pairs), optimal_batch_size):
                batch_pairs = sentence_pairs[i:i + optimal_batch_size]
                batch_scores = self._model.predict(batch_pairs)
                all_scores.extend(batch_scores.tolist())
        
        processing_time = time.time() - start_time
        throughput = len(documents) / processing_time
        
        logger.info(f"[경량화] Cross-encoder 처리 완료: {len(documents)}개 문서, "
                   f"배치크기: {optimal_batch_size}, 처리시간: {processing_time:.2f}s, "
                   f"처리량: {throughput:.1f} docs/sec")
        
        return all_scores

    def _get_optimal_batch_size(self, num_documents: int) -> int:
        """동적 배치 크기 결정"""
        
        # 기본 배치 크기
        base_batch_size = min(self.max_batch_size, num_documents)
        
        # 메모리 상황 고려
        if self._device == "cuda":
            gpu_memory_free = (torch.cuda.get_device_properties(0).total_memory - 
                             torch.cuda.memory_allocated()) / 1024**3
            
            if gpu_memory_free < 1.0:  # 1GB 미만
                optimal_batch_size = max(1, base_batch_size // 4)
                logger.info(f"[경량화] GPU 메모리 부족 ({gpu_memory_free:.1f}GB), "
                           f"배치 크기 축소: {base_batch_size} → {optimal_batch_size}")
            elif gpu_memory_free < 2.0:  # 2GB 미만
                optimal_batch_size = max(1, base_batch_size // 2)
                logger.info(f"[경량화] GPU 메모리 제한적 ({gpu_memory_free:.1f}GB), "
                           f"배치 크기 조정: {base_batch_size} → {optimal_batch_size}")
            else:
                optimal_batch_size = base_batch_size
                
        else:
            # CPU 메모리 체크
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:  # 90% 이상
                optimal_batch_size = max(1, base_batch_size // 4)
                logger.info(f"[경량화] CPU 메모리 부족 ({memory_percent}%), "
                           f"배치 크기 축소: {base_batch_size} → {optimal_batch_size}")
            elif memory_percent > 85:  # 85% 이상
                optimal_batch_size = max(1, base_batch_size // 2)
                logger.info(f"[경량화] CPU 메모리 제한적 ({memory_percent}%), "
                           f"배치 크기 조정: {base_batch_size} → {optimal_batch_size}")
            else:
                optimal_batch_size = base_batch_size
        
        # 문서 수에 따른 추가 조정
        if num_documents <= 3:
            optimal_batch_size = min(optimal_batch_size, 4)  # 소량 처리 시 작은 배치
        elif num_documents >= 50:
            optimal_batch_size = min(optimal_batch_size, self.max_batch_size)  # 대량 처리 시 큰 배치
        
        return optimal_batch_size

    def benchmark_batch_sizes(self, query: str, documents: List[str], 
                            test_batch_sizes: List[int] = None) -> dict:
        """다양한 배치 크기별 성능 벤치마크"""
        if test_batch_sizes is None:
            test_batch_sizes = [1, 4, 8, 16, 32]
        
        if not documents:
            return {}
        
        logger.info(f"[경량화] Cross-encoder 배치 크기 벤치마크 시작: {len(documents)}개 문서")
        
        results = {}
        sentence_pairs = [[query, doc] for doc in documents]
        
        for batch_size in test_batch_sizes:
            if batch_size > len(documents):
                continue
                
            try:
                start_time = time.time()
                all_scores = []
                
                with torch.no_grad():
                    for i in range(0, len(sentence_pairs), batch_size):
                        batch_pairs = sentence_pairs[i:i + batch_size]
                        batch_scores = self._model.predict(batch_pairs)
                        all_scores.extend(batch_scores.tolist())
                
                processing_time = time.time() - start_time
                throughput = len(documents) / processing_time
                memory_usage = self._get_memory_usage()
                
                results[batch_size] = {
                    "processing_time": processing_time,
                    "throughput": throughput,
                    "memory_usage_mb": memory_usage,
                    "scores_sample": all_scores[:3]  # 처음 3개 점수만 저장
                }
                
                logger.info(f"배치크기 {batch_size}: {processing_time:.2f}s, "
                           f"{throughput:.1f} docs/sec, {memory_usage:.1f}MB")
                           
            except Exception as e:
                logger.warning(f"배치크기 {batch_size} 테스트 실패: {e}")
                results[batch_size] = {"error": str(e)}
        
        # 최적 배치 크기 추천
        if results:
            best_batch_size = max(results.keys(), 
                                key=lambda x: results[x].get("throughput", 0))
            logger.info(f"[경량화] 최적 배치 크기 추천: {best_batch_size}")
            results["recommended_batch_size"] = best_batch_size
        
        return results

    def get_model_info(self) -> dict:
        """모델 정보 및 최적화 상태 반환"""
        info = {
            "model_name": self.model_name,
            "device": self._device,
            "quantization_enabled": self.enable_quantization,
            "max_batch_size": self.max_batch_size,
            "memory_usage_mb": self._get_memory_usage(),
        }
        
        if self._device == "cuda":
            info["gpu_memory_total"] = torch.cuda.get_device_properties(0).total_memory / 1024**3
            info["gpu_memory_allocated"] = torch.cuda.memory_allocated() / 1024**3
        
        return info

if __name__ == "__main__":
    logger.info("[경량화] OptimizedCrossEncoderModel 테스트 시작...")

    # 모델 초기화
    model = OptimizedCrossEncoderModel(enable_quantization=True, max_batch_size=16)

    # 테스트 데이터
    test_query = "부동산 매매 계약 해지"
    test_documents = [
        "부동산 매매 계약은 당사자 일방이 재산권을 상대방에게 이전할 것을 약정하고 상대방이 그 대금을 지급할 것을 약정함으로써 효력이 생긴다.",
        "계약 해지는 당사자 일방의 의사표시로 가능하며, 해지 시에는 원상회복의 의무가 발생한다.",
        "임대차 계약은 임대인이 임차인에게 목적물을 사용, 수익하게 하고 임차인이 이에 대한 차임을 지급할 것을 약정함으로써 성립한다.",
        "매매계약의 해제는 계약 당사자가 합의하거나 법정 해제 사유가 있을 때 가능하다.",
        "부동산 거래에서 계약금은 계약 성립의 증거이자 계약 이행을 담보하는 역할을 한다."
    ]

    # 기본 점수 계산 테스트
    scores = model.get_cross_encoder_scores(test_query, test_documents)
    logger.info(f"점수 계산 결과: {len(scores)}개 점수")
    for i, score in enumerate(scores):
        logger.info(f"  문서 {i+1}: {score:.4f}")

    # 배치 크기 벤치마크
    benchmark_results = model.benchmark_batch_sizes(test_query, test_documents, [1, 2, 4, 8])
    logger.info(f"벤치마크 결과: {benchmark_results}")

    # 모델 정보 출력
    model_info = model.get_model_info()
    logger.info(f"모델 정보: {model_info}")

    logger.info("[경량화] 테스트 완료")