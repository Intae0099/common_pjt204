import os
import json
import glob
import pickle
from rank_bm25 import BM25Okapi
from tqdm import tqdm
import re

from utils.logger import get_logger

logger = get_logger(__name__)

# 환경변수로 Kiwi 완전 비활성화
FORCE_SIMPLE_TOKENIZER = os.environ.get('FORCE_SIMPLE_TOKENIZER', 'false').lower() == 'true'

if FORCE_SIMPLE_TOKENIZER:
    logger.info('환경변수로 Kiwi 비활성화됨. 단순 토크나이저 사용.')
    KIWI_AVAILABLE = False
else:
    try:
        from kiwipiepy import Kiwi
        KIWI_AVAILABLE = True
    except:
        KIWI_AVAILABLE = False
        logger.warning('Kiwi 설치되지 않음. 단순 토크나이저 사용.')

class BM25Service:
    """BM25 알고리즘을 사용하여 판례를 검색하는 서비스."""
    _instance = None
    CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "preprocessed", "bm25_cache.pkl")

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BM25Service, cls).__new__(cls)
        return cls._instance

    def __init__(self, data_dir=None):
        if hasattr(self, '_initialized'):
            return
        
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "preprocessed")
        else:
            self.data_dir = data_dir
        self.bm25 = None
        self.cases = []

        if os.path.exists(self.CACHE_PATH):
            logger.info(f"캐시 파일({self.CACHE_PATH})을 로드합니다.")
            self._load_from_cache()
        else:
            logger.warning("BM25 캐시 파일이 없습니다. 새로 생성합니다.")
            self._build_and_save_cache()
            self._load_from_cache()
            
        self._initialized = True
        logger.info("BM25Service 초기화가 완료되었습니다.")

    def _simple_tokenizer(self, text):
        """개선된 한국어 단순 토크나이저"""
        if not text:
            return []
        
        # 한글, 영어, 숫자만 추출
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}|[0-9]+', text)
        
        # 법률 용어 우선 처리
        legal_terms = {'형법', '민법', '횡령', '배임', '사기', '손해배상', '계약', '이혼', '상속', '교통사고'}
        result = []
        for token in tokens:
            if token in legal_terms or len(token) >= 2:
                result.append(token)
        
        return list(dict.fromkeys(result))  # 중복 제거

    def _load_from_cache(self):
        """디스크에서 미리 계산된 캐시를 로드합니다."""
        with open(self.CACHE_PATH, 'rb') as f:
            cached_data = pickle.load(f)
            self.bm25 = cached_data['bm25']
            self.cases = cached_data['cases']
        logger.info(f"캐시 로드 완료. {len(self.cases)}개의 판례가 준비되었습니다.")

    def _build_and_save_cache(self):
        """판례 데이터를 로드하여 BM25 모델을 만들고 캐시 파일로 저장합니다."""
        if KIWI_AVAILABLE and not FORCE_SIMPLE_TOKENIZER:
            try:
                tokenizer = Kiwi()
                logger.info("Kiwi 형태소 분석기를 사용합니다.")
            except Exception as e:
                logger.error(f"Kiwi 초기화 실패: {e}")
                tokenizer = None
        else:
            tokenizer = None
            logger.info("단순 토크나이저를 사용합니다.")
        
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
                    return self._simple_tokenizer(text)
                
                text = re.sub(r'[^\w\s가-힣]', ' ', text)
                tokens = tokenizer.tokenize(text)
                return [token.form for token in tokens if token.tag in ['NNG', 'NNP'] and len(token.form) > 1]
            except Exception as e:
                logger.warning(f"토큰화 실패 (fallback): {e}")
                return self._simple_tokenizer(text)

        try:
            tokenized_corpus = []
            for i, doc in enumerate(tqdm(corpus, desc="Corpus 토큰화")):
                try:
                    tokens = tokenize_fn(doc)
                    tokenized_corpus.append(tokens)
                except Exception as e:
                    logger.warning(f"문서 {i} 토큰화 실패: {e}")
                    tokenized_corpus.append([])
            
            bm25_model = BM25Okapi(tokenized_corpus)

            with open(self.CACHE_PATH, 'wb') as f:
                pickle.dump({'bm25': bm25_model, 'cases': cases_data}, f)
            logger.info(f"BM25 캐시 파일이 {self.CACHE_PATH}에 저장되었습니다.")
            
        except Exception as e:
            logger.error(f"BM25 모델 생성 중 오류 발생: {e}")
            raise

    def search(self, query: str, top_n: int = 10):
        """주어진 쿼리로 판례를 검색하고 상위 N개의 결과를 반환합니다."""
        if not self.bm25:
            logger.error("BM25 모델이 초기화되지 않았습니다.")
            return []
            
        logger.debug(f"BM25 검색 수행: query='{query}', top_n={top_n}")
        
        if KIWI_AVAILABLE and not FORCE_SIMPLE_TOKENIZER:
            try:
                tokenizer = Kiwi()
            except Exception as e:
                logger.warning(f"Kiwi 초기화 실패: {e}")
                tokenizer = None
        else:
            tokenizer = None
            
        def tokenize_fn(text):
            try:
                if tokenizer is None:
                    return self._simple_tokenizer(text)
                
                text = re.sub(r'[^\w\s가-힣]', ' ', text)
                tokens = tokenizer.tokenize(text)
                return [token.form for token in tokens if token.tag in ['NNG', 'NNP'] and len(token.form) > 1]
            except Exception as e:
                logger.warning(f"토큰화 실패 (fallback): {e}")
                return self._simple_tokenizer(text)

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
