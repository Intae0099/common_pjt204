from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class StreamChunk(BaseModel):
    reply: str
