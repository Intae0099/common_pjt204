
import os
import json
import glob
import pickle  # pickle 추가
from kiwipiepy import Kiwi
from rank_bm25 import BM25Okapi
from tqdm import tqdm
import re

from utils.logger import get_logger

logger = get_logger(__name__)

class BM25Service:
    """
    BM25 알고리즘을 사용하여 판례를 검색하는 서비스.
    초기화 시 캐시된 모델을 로드하며, 캐시가 없을 경우 자동으로 생성합니다.
    """
    _instance = None
    CACHE_PATH = "F:/S13P11B204/ai/data/preprocessed/bm25_cache.pkl"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BM25Service, cls).__new__(cls)
        return cls._instance

    def __init__(self, data_dir="F:/S13P11B204/ai/data/preprocessed"):
        if hasattr(self, '_initialized'):
            return
        
        self.data_dir = data_dir
        self.bm25 = None
        self.cases = []

        if os.path.exists(self.CACHE_PATH):
            logger.info(f"캐시 파일({self.CACHE_PATH})을 로드합니다.")
            self._load_from_cache()
        else:
            logger.warning("BM25 캐시 파일이 없습니다. 새로 생성합니다. (이 작업은 몇 분 정도 소요될 수 있습니다)")
            self._build_and_save_cache()
            self._load_from_cache()
            
        self._initialized = True
        logger.info("BM25Service 초기화가 완료되었습니다.")

    def _load_from_cache(self):
        """디스크에서 미리 계산된 캐시를 로드합니다."""
        with open(self.CACHE_PATH, 'rb') as f:
            cached_data = pickle.load(f)
            self.bm25 = cached_data['bm25']
            self.cases = cached_data['cases']
        logger.info(f"캐시 로드 완료. {len(self.cases)}개의 판례가 준비되었습니다.")

    def _build_and_save_cache(self):
        """판례 데이터를 로드하여 BM25 모델을 만들고 캐시 파일로 저장합니다."""
        try:
            tokenizer = Kiwi()
        except Exception as e:
            logger.error(f"Kiwi 형태소 분석기 초기화 실패: {e}")
            logger.warning("형태소 분석기 없이 단순 분리 방식으로 fallback합니다.")
            tokenizer = None
        
        json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
        if not json_files:
            logger.error(f"{self.data_dir} 에서 판례 파일을 찾을 수 없습니다.")
            return

        corpus = []
        cases_data = []
        for file_path in tqdm(json_files, desc="판례 데이터 로딩"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    case_data = json.load(f)
                
                title = case_data.get('title', '')
                issue = case_data.get('issue', '')
                summary = case_data.get('summary', '')
                full_text = ' '.join(filter(None, [title, issue, summary]))
                
                if full_text.strip():
                    cases_data.append(case_data)
                    corpus.append(full_text)
            except Exception as e:
                logger.error(f"판례 로딩 중 오류 발생 {file_path}: {e}")

        logger.info(f"총 {len(corpus)}개의 판례로 BM25 모델을 학습합니다.")
        
        def tokenize_fn(text):
            try:
                if tokenizer is None:
                    # 형태소 분석기가 없을 경우 단순 분리
                    text = re.sub(r'[^\w\s]', '', text)
                    return [word for word in text.split() if len(word.strip()) > 1]
                
                text = re.sub(r'[^\w\s]', '', text)
                tokens = tokenizer.tokenize(text)
                return [token.form for token in tokens if token.tag in ['NNG', 'NNP']]
            except Exception as e:
                logger.warning(f"토큰화 실패 (fallback to simple split): {e}")
                # 형태소 분석 실패 시 단순 공백 분리로 fallback
                text = re.sub(r'[^\w\s]', '', text)
                return [word for word in text.split() if len(word.strip()) > 1]

        try:
            tokenized_corpus = []
            for i, doc in enumerate(tqdm(corpus, desc="Corpus 토큰화")):
                try:
                    tokens = tokenize_fn(doc)
                    tokenized_corpus.append(tokens)
                except Exception as e:
                    logger.warning(f"문서 {i} 토큰화 실패: {e}, 빈 토큰 리스트로 대체")
                    tokenized_corpus.append([])
            
            bm25_model = BM25Okapi(tokenized_corpus)

            # 캐시 데이터 저장
            with open(self.CACHE_PATH, 'wb') as f:
                pickle.dump({'bm25': bm25_model, 'cases': cases_data}, f)
            logger.info(f"BM25 캐시 파일이 {self.CACHE_PATH}에 저장되었습니다.")
            
        except Exception as e:
            logger.error(f"BM25 모델 생성 중 심각한 오류 발생: {e}")
            logger.error("캐시 생성을 중단합니다.")
            raise

    def search(self, query: str, top_n: int = 10) -> list[dict]:
        """
        주어진 쿼리로 판례를 검색하고 상위 N개의 결과를 반환합니다.
        """
        if not self.bm25:
            logger.error("BM25 모델이 초기화되지 않았습니다.")
            return []
            
        logger.debug(f"BM25 검색 수행: query='{query}', top_n={top_n}")
        
        # 토크나이저 안전한 초기화
        try:
            tokenizer = Kiwi()
        except Exception as e:
            logger.warning(f"Kiwi 형태소 분석기 초기화 실패: {e}, 단순 분리 방식 사용")
            tokenizer = None
            
        def tokenize_fn(text):
            try:
                if tokenizer is None:
                    # 형태소 분석기가 없을 경우 단순 분리
                    text = re.sub(r'[^\w\s]', '', text)
                    return [word for word in text.split() if len(word.strip()) > 1]
                
                text = re.sub(r'[^\w\s]', '', text)
                tokens = tokenizer.tokenize(text)
                return [token.form for token in tokens if token.tag in ['NNG', 'NNP']]
            except Exception as e:
                logger.warning(f"토큰화 실패 (fallback to simple split): {e}")
                # 형태소 분석 실패 시 단순 공백 분리로 fallback
                text = re.sub(r'[^\w\s]', '', text)
                return [word for word in text.split() if len(word.strip()) > 1]

        try:
            tokenized_query = tokenize_fn(query)
            
            doc_scores = self.bm25.get_scores(tokenized_query)
            
            scored_indices = sorted(enumerate(doc_scores), key=lambda x: x[1], reverse=True)
            
            top_indices = [idx for idx, score in scored_indices[:top_n] if score > 0]
            
            results = [self.cases[i] for i in top_indices]
            logger.debug(f"{len(results)}개의 검색 결과를 반환합니다.")
            
            return results
            
        except Exception as e:
            logger.error(f"BM25 검색 중 오류 발생: {e}")
            return []

