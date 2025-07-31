from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from app.api.dependencies import get_current_user
from app.api.schemas.chat import ChatRequest
from services.chat_service import stream_chat_response

router = APIRouter()


@router.post(
    "/chat/stream",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def stream_chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        stream_chat_response(request), media_type="text/event-stream"
    )
