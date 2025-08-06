import sys
import os
from typing import Optional
from openai import OpenAI, AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from config.settings import get_llm_settings
from utils.logger import get_logger

logger = get_logger(__name__)

# --- 설정값 로드 --- #
llm_settings = get_llm_settings()

# --- 클라이언트 초기화 --- #
def _validate_settings():
    """LLM 설정 검증"""
    if not llm_settings.gms_key:
        raise ValueError(
            "GMS_KEY(또는 OPENAI_API_KEY)가 설정되지 않았습니다. "
            "프로젝트의 `config/.env` 파일에 GMS_KEY를 설정해주세요."
        )

_validate_settings()

# OpenAI 클라이언트 설정 준비
client_kwargs = {
    "api_key": llm_settings.gms_key,
}

# GMS 기본 URL이 있는 경우 추가 (선택사항)
gms_base_url = os.getenv("GMS_BASE_URL")
if gms_base_url:
    client_kwargs["base_url"] = gms_base_url
    logger.info(f"Using GMS base URL: {gms_base_url}")
else:
    logger.info("Using default OpenAI API endpoint")

# 동기 클라이언트
client = OpenAI(**client_kwargs)

# 비동기 클라이언트
async_client = AsyncOpenAI(**client_kwargs)

@retry(
    wait=wait_random_exponential(min=1, max=60), 
    stop=stop_after_attempt(3)  # llm_settings.max_retries
)
def call_gpt4o(
    messages, 
    temperature: float = 0.3, 
    max_tokens: int = 2048, 
    stream: bool = False,
    model: Optional[str] = None
):
    """
    (동기) OpenAI API를 통해 GPT 모델을 호출하는 함수입니다.
    """
    model_name = model or os.getenv("MODEL_NAME", "gpt-4o-mini")
    
    try:
        logger.debug(f"Calling OpenAI API with model: {model_name}")
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        if stream:
            return response
        else:
            return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API 동기 호출 중 오류 발생: {e}")
        raise

@retry(
    wait=wait_random_exponential(min=1, max=60), 
    stop=stop_after_attempt(3)  # llm_settings.max_retries
)
async def async_call_gpt4o(
    messages, 
    temperature: float = 0.3, 
    max_tokens: int = 2048, 
    stream: bool = False,
    model: Optional[str] = None
):
    """
    (비동기) OpenAI API를 통해 GPT 모델을 호출하는 함수입니다.
    스트리밍 호출을 지원합니다.
    """
    model_name = model or os.getenv("MODEL_NAME", "gpt-4o-mini")
    
    try:
        logger.debug(f"Calling OpenAI API (async) with model: {model_name}")
        response = await async_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        return response
    except Exception as e:
        logger.error(f"OpenAI API 비동기 호출 중 오류 발생: {e}")
        raise


def get_async_openai_client() -> AsyncOpenAI:
    """비동기 OpenAI 클라이언트를 반환합니다."""
    return async_client


def get_sync_openai_client() -> OpenAI:
    """동기 OpenAI 클라이언트를 반환합니다."""
    return client
