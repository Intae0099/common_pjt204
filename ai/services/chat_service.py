import inspect
from app.api.schemas.chat import ChatRequest, StreamChunk
from llm.prompt_templates.chat_prompts import ChatPromptTemplate
from collections import deque
from typing import Deque, Dict, Tuple
from openai import OpenAI
from utils.logger import get_logger

logger = get_logger(__name__)

class ChatService:
    def __init__(self, llm_client: OpenAI):
        self.llm_client = llm_client
        self.chat_histories: Dict[str, Deque[Tuple[str, str]]] = {}
        self.MAX_HISTORY_TOKENS = 3000

    async def stream_chat_response(self, req: ChatRequest, user_id: str):
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = deque()
        history = self.chat_histories[user_id]

        messages = ChatPromptTemplate.build_messages(history, req.message)
        history.append(("user", req.message))

        assistant_reply = ""
        try:
            stream = await self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True
            )
            async for chunk in stream:
                chunk_content = chunk.choices[0].delta.content or ""
                assistant_reply += chunk_content
                yield f"data: {StreamChunk(reply=chunk_content).model_dump_json()}\n\n"

        except Exception as e:
            logger.error(f"LLM stream error for user {user_id}: {e}")
            yield f"data: {{'error': 'An error occurred during the stream.'}}\n\n"

        finally:
            if assistant_reply:
                history.append(("assistant", assistant_reply))
                # 토큰 제한 초과 시 (user, assistant) 쌍으로 가장 오래된 대화부터 제거
                total = sum(len(c) for _, c in history)
                while total > self.MAX_HISTORY_TOKENS and len(history) >= 2:
                    user_msg = history.popleft()
                    assistant_msg = history.popleft()
                    total -= (len(user_msg[1]) + len(assistant_msg[1]))
            yield "data: [DONE]\n\n"

