from collections import deque
from typing import Deque, Dict, List, Tuple
from app.api.schemas.chat import ChatRequest, StreamChunk
from llm.clients.openai_client import call_gpt4o
from utils.logger import get_logger

logger = get_logger(__name__)

# 사용자별 대화 이력을 저장하는 인메모리 딕셔너리
chat_histories: Dict[str, Deque[Tuple[str, str]]] = {}
# 대화 이력의 최대 토큰 수를 설정 (간단히 문자 수로 근사)
MAX_HISTORY_TOKENS = 3000

def _prune_history_by_tokens(history: Deque[Tuple[str, str]], max_tokens: int):
    """대화 이력의 총 토큰(문자) 수가 max_tokens를 넘지 않도록 가장 오래된 대화부터 제거합니다."""
    current_tokens = sum(len(content) for _, content in history)
    while current_tokens > max_tokens and history:
        role, content = history.popleft()
        current_tokens -= len(content)

def _build_messages(history: Deque[Tuple[str, str]], new_message: str) -> List[Dict[str, str]]:
    """LLM에 전달할 messages 리스트를 생성합니다."""
    messages = [{"role": role, "content": content} for role, content in history]
    messages.append({"role": "user", "content": new_message})
    return messages

async def stream_chat_response(req: ChatRequest, user_id: str):
    """
    사용자 메시지를 받아 LLM 스트리밍 응답을 생성하고, 대화 이력을 토큰 기준으로 관리합니다.
    """
    if user_id not in chat_histories:
        chat_histories[user_id] = deque()
    history = chat_histories[user_id]

    messages = _build_messages(history, req.message)
    
    history.append(("user", req.message))

    assistant_reply = ""
    try:
        stream = call_gpt4o(messages, stream=True)
        for chunk in stream:
            chunk_content = chunk.choices[0].delta.content or ""
            assistant_reply += chunk_content
            yield f"data: {StreamChunk(reply=chunk_content).model_dump_json()}\n\n"

    except Exception as e:
        logger.error(f"LLM stream error for user {user_id}: {e}")
    finally:
        if assistant_reply:
            history.append(("assistant", assistant_reply))
            # 대화 종료 후 토큰 수 기준으로 이력 정리
            _prune_history_by_tokens(history, MAX_HISTORY_TOKENS)
        
        yield "data: [DONE]\n\n"