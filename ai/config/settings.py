"""
중앙화된 설정 관리 모듈
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 경로를 절대경로로 설정
ENV_FILE_PATH = Path(__file__).parent / ".env"

# .env 파일을 명시적으로 로드 (환경변수 우선)
load_result = load_dotenv(ENV_FILE_PATH, override=False)


class DatabaseSettings(BaseSettings):
    """데이터베이스 관련 설정"""
    model_config = {
        "extra": "ignore"
    }
    
    user: str
    password: str
    host: str
    port: int
    name: str
    
    def __init__(self, **data):
        # 환경변수에서 직접 값 로드
        if not data:
            data = {
                'user': os.environ.get('DB_USER', 'postgres'),
                'password': os.environ.get('DB_PASSWORD', ''),
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': int(os.environ.get('DB_PORT', '5432')),
                'name': os.environ.get('DB_NAME', 'postgres')
            }
        super().__init__(**data)
    
    @property
    def url(self) -> str:
        """SQLAlchemy 데이터베이스 URL 생성"""
        if not all([self.user, self.password, self.host, self.name]):
            raise ValueError("데이터베이스 연결에 필요한 환경변수가 설정되지 않았습니다.")
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def psycopg2_params(self) -> dict:
        """psycopg2 연결 파라미터"""
        if not all([self.user, self.password, self.host, self.name]):
            raise ValueError("데이터베이스 연결에 필요한 환경변수가 설정되지 않았습니다.")
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.name,
            "user": self.user,
            "password": self.password
        }


class LLMSettings(BaseSettings):
    """LLM 관련 설정"""
    model_config = {
        "extra": "ignore"
    }
    
    gms_key: str
    max_history_tokens: int
    max_retries: int
    embedding_model_name: str
    cross_encoder_model_name: str
    
    def __init__(self, **data):
        if not data:
            data = {
                'gms_key': os.environ.get('GMS_KEY', ''),
                'max_history_tokens': int(os.environ.get('MAX_HISTORY_TOKENS', '3000')),
                'max_retries': int(os.environ.get('LLM_MAX_RETRIES', '3')),
                'embedding_model_name': os.environ.get('EMBEDDING_MODEL_NAME', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),
                'cross_encoder_model_name': os.environ.get('CROSS_ENCODER_MODEL_NAME', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
            }
        super().__init__(**data)


class APISettings(BaseSettings):
    """API 관련 설정"""
    model_config = {
        "extra": "ignore"
    }
    
    host: str
    port: int
    reload: bool
    cors_origins_str: str
    
    def __init__(self, **data):
        if not data:
            data = {
                'host': os.environ.get('API_HOST', '0.0.0.0'),
                'port': int(os.environ.get('API_PORT', '8000')),
                'reload': os.environ.get('API_RELOAD', 'true').lower() == 'true',
                'cors_origins_str': os.environ.get('CORS_ORIGINS', 'http://localhost:5173,https://i13b204.p.ssafy.io/')
            }
        super().__init__(**data)
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS 허용 도메인 리스트를 반환"""
        if isinstance(self.cors_origins_str, str):
            return [origin.strip() for origin in self.cors_origins_str.split(',') if origin.strip()]
        return self.cors_origins_str


class SearchSettings(BaseSettings):
    """검색 관련 설정"""
    model_config = {
        "extra": "ignore"
    }
    
    default_page_size: int
    max_page_size: int
    vector_search_top_k: int
    use_rerank_default: bool
    
    def __init__(self, **data):
        if not data:
            data = {
                'default_page_size': int(os.environ.get('DEFAULT_PAGE_SIZE', '10')),
                'max_page_size': int(os.environ.get('MAX_PAGE_SIZE', '50')),
                'vector_search_top_k': int(os.environ.get('VECTOR_SEARCH_TOP_K', '20')),
                'use_rerank_default': os.environ.get('USE_RERANK_DEFAULT', 'true').lower() == 'true'
            }
        super().__init__(**data)


class LoggingSettings(BaseSettings):
    """로깅 관련 설정"""
    model_config = {
        "extra": "ignore"
    }
    
    level: str
    format: str
    file_path: Optional[str]
    
    def __init__(self, **data):
        if not data:
            data = {
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
                'format': os.environ.get('LOG_FORMAT', '[%(asctime)s][%(levelname)s][%(name)s] %(message)s'),
                'file_path': os.environ.get('LOG_FILE_PATH')
            }
        super().__init__(**data)


class Settings(BaseSettings):
    """전체 애플리케이션 설정"""
    model_config = {
        "extra": "ignore"
    }

    
    database: DatabaseSettings = DatabaseSettings()
    llm: LLMSettings = LLMSettings()
    api: APISettings = APISettings()
    search: SearchSettings = SearchSettings()
    logging: LoggingSettings = LoggingSettings()


# 싱글톤 패턴으로 설정 인스턴스 제공
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """설정 인스턴스를 반환 (싱글톤)"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


# 편의를 위한 개별 설정 접근 함수들
def get_database_settings() -> DatabaseSettings:
    return get_settings().database


def get_llm_settings() -> LLMSettings:
    return get_settings().llm


def get_api_settings() -> APISettings:
    return get_settings().api


def get_search_settings() -> SearchSettings:
    return get_settings().search


def get_logging_settings() -> LoggingSettings:
    return get_settings().logging