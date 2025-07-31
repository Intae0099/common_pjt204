import asyncio
from app.api.schemas.chat import ChatRequest, StreamChunk


async def stream_chat_response(req: ChatRequest):
    # Simulate LLM streaming response
    for chunk in ["Hello", ", ", "world", "!"]:
        await asyncio.sleep(0.1)
        yield f"data: {StreamChunk(reply=chunk).model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"

