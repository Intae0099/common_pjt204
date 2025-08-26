import os
import json
import glob
import pickle
from rank_bm25 import BM25Okapi
from tqdm import tqdm
import re

from utils.logger import get_logger

logger = get_logger(__name__)

# Kiwi 완전 제거 - 단순 토크나이저만 사용
logger.info('Kiwi 완전 제거됨. 한국어 최적화된 단순 토크나이저 사용.')

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

    def _korean_tokenizer(self, text):
        """한국어 법률 문서에 최적화된 토크나이저"""
        if not text:
            return []
        
        # 1. 텍스트 정리
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 2. 토큰 추출 (한글 2글자 이상, 영어 2글자 이상, 숫자)
        tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}|[0-9]+', text)
        
        # 3. 법률 용어 사전 (확장)
        legal_terms = {
            # 기본 법령
            '형법', '민법', '상법', '헌법', '행정법', '노동법', '세법', '민사법', '형사법',
            # 범죄 유형
            '횡령', '배임', '사기', '절도', '강도', '살인', '폭행', '협박', '강간', '성폭행',
            '뇌물', '공갈', '위조', '변조', '위증', '무고', '명예훼손', '모독',
            # 민사 분야
            '손해배상', '계약', '불법행위', '과실', '고의', '위법', '채무', '채권',
            '임대차', '매매', '증여', '담보', '저당', '질권',
            # 가족법
            '이혼', '상속', '양육권', '친권', '재산분할', '위자료', '양육비',
            # 기타
            '교통사고', '의료사고', '산업재해', '보험', '세금'
        }
        
        # 4. 토큰 필터링 및 우선순위 처리
        result = []
        for token in tokens:
            # 법률 용어는 무조건 포함
            if token in legal_terms:
                result.append(token)
            # 2글자 이상 일반 단어
            elif len(token) >= 2:
                # 너무 긴 단어는 제외 (오타나 이상한 문자열)
                if len(token) <= 15:
                    result.append(token)
        
        # 5. 중복 제거하면서 순서 유지
        return list(dict.fromkeys(result))

    def _load_from_cache(self):
        """디스크에서 미리 계산된 캐시를 로드합니다."""
        with open(self.CACHE_PATH, 'rb') as f:
            cached_data = pickle.load(f)
            self.bm25 = cached_data['bm25']
            self.cases = cached_data['cases']
        logger.info(f"캐시 로드 완료. {len(self.cases)}개의 판례가 준비되었습니다.")

    def _build_and_save_cache(self):
        """판례 데이터를 로드하여 BM25 모델을 만들고 캐시 파일로 저장합니다."""
        logger.info("한국어 최적화 토크나이저를 사용하여 BM25 모델을 생성합니다.")
        
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
        
        # 토큰화 실행
        try:
            tokenized_corpus = []
            for i, doc in enumerate(tqdm(corpus, desc="문서 토큰화")):
                try:
                    tokens = self._korean_tokenizer(doc)
                    tokenized_corpus.append(tokens)
                except Exception as e:
                    logger.warning(f"문서 {i} 토큰화 실패: {e}")
                    tokenized_corpus.append([])
            
            bm25_model = BM25Okapi(tokenized_corpus)

            # 캐시 저장
            os.makedirs(os.path.dirname(self.CACHE_PATH), exist_ok=True)
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
        
        try:
            # 쿼리 토큰화
            tokenized_query = self._korean_tokenizer(query)
            
            if not tokenized_query:
                logger.warning(f"쿼리 '{query}'가 토큰화 결과 비어있음")
                return []
            
            # BM25 점수 계산
            doc_scores = self.bm25.get_scores(tokenized_query)
            
            # 점수 순 정렬
            scored_indices = sorted(enumerate(doc_scores), key=lambda x: x[1], reverse=True)
            
            # 상위 N개 추출 (점수가 0보다 큰 것만)
            top_indices = [idx for idx, score in scored_indices[:top_n] if score > 0]
            
            results = [self.cases[i] for i in top_indices]
            logger.debug(f"{len(results)}개의 검색 결과를 반환합니다.")
            
            return results
            
        except Exception as e:
            logger.error(f"BM25 검색 중 오류 발생: {e}")
            return []
