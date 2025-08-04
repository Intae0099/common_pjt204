import os
import sys
from openai import OpenAI, AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from pathlib import Path

# .env 파일 로드를 애플리케이션 시작점(run_analysis.py)에서 처리하므로,
# 여기서는 로드된 환경 변수를 사용하기만 합니다.
from dotenv import load_dotenv
dotenv_path = Path(__file__).resolve().parents[2] / "config" / ".env"
load_dotenv(dotenv_path)

# --- 설정값 로드 --- #
gms_api_key = os.getenv("GMS_KEY")
gms_base_url = os.getenv("GMS_BASE_URL")

# --- 클라이언트 초기화 --- #
if not gms_api_key or not gms_base_url:
    raise ValueError(
        "GMS_API_KEY 또는 GMS_API_BASE_URL이 설정되지 않았습니다. "
        "프로젝트의 `ai/config/.env` 파일을 올바르게 설정했는지 확인해주세요."
    )

# 동기 클라이언트
client = OpenAI(
    api_key=gms_api_key,
    base_url=gms_base_url,
)

# 비동기 클라이언트
async_client = AsyncOpenAI(
    api_key=gms_api_key,
    base_url=gms_base_url,
)

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
def call_gpt4o(messages, temperature=0.3, max_tokens=2048, stream=False):
    """
    (동기) GMS를 통해 GPT-4o-mini 모델을 호출하는 함수입니다.
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
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
        print(f"GMS API 동기 호출 중 오류 발생: {e}", file=sys.stderr)
        raise

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
async def async_call_gpt4o(messages, temperature=0.3, max_tokens=2048, stream=False):
    """
    (비동기) GMS를 통해 GPT-4o-mini 모델을 호출하는 함수입니다.
    스트리밍 호출을 지원합니다.
    """
    try:
        response = await async_client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        return response
    except Exception as e:
        print(f"GMS API 비동기 호출 중 오류 발생: {e}", file=sys.stderr)
        raise
