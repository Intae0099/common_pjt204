import os
import sys
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from pathlib import Path

# .env 파일 로드를 애플리케이션 시작점(run_analysis.py)에서 처리하므로,
# 여기서는 로드된 환경 변수를 사용하기만 합니다.
from dotenv import load_dotenv
dotenv_path = Path(__file__).resolve().parents[2] / "config" / ".env"
# print(f"[Config] Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path)

# --- 설정값 로드 및 디버깅 --- #
gms_api_key = os.getenv("GMS_KEY")
gms_base_url = os.getenv("GMS_BASE_URL")

# 프로그램 실행 시 터미널에 현재 설정 상태를 출력하여 확인을 돕습니다.
# print("-" * 50, file=sys.stderr)
# print("[[ openai_client.py Configuration Check ]]", file=sys.stderr)
# print(f"GMS_API_KEY loaded: {'Yes' if gms_api_key else 'No - PLEASE CHECK .env FILE'}", file=sys.stderr)
# print(f"GMS_API_BASE_URL loaded: {'Yes' if gms_base_url else 'No - PLEASE CHECK .env FILE'}", file=sys.stderr)
# print(f" -> Endpoint URL: {gms_base_url}", file=sys.stderr)
# print("-" * 50, file=sys.stderr)


# --- 클라이언트 초기화 --- #
# 설정값이 하나라도 빠졌으면, 더 진행하지 않고 명확한 오류를 발생시킵니다.
if not gms_api_key or not gms_base_url:
    raise ValueError(
        "GMS_API_KEY 또는 GMS_API_BASE_URL이 설정되지 않았습니다. "
        "프로젝트의 `ai/config/.env` 파일을 올바르게 설정했는지 확인해주세요."
    )

# 확인된 설정값으로 GMS API 클라이언트를 초기화합니다.
client = OpenAI(
    api_key=gms_api_key,
    base_url=gms_base_url,
)

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
def call_gpt4o(messages, temperature=0.3, max_tokens=2048, stream=False):
    """
    GMS를 통해 GPT-4o-mini 모델을 호출하는 함수입니다.
    스트리밍 호출을 지원합니다.
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
        print(f"GMS API 호출 중 오류 발생: {e}", file=sys.stderr)
        raise