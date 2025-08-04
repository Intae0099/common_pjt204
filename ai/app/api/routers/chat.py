from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from app.api.dependencies import get_current_user, get_chat_service
from app.api.schemas.chat import ChatRequest
from services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/chat/stream",
    status_code=status.HTTP_200_OK,
)
async def stream_chat_endpoint(
    request: ChatRequest, 
    user_id: str = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    return StreamingResponse(
        chat_service.stream_chat_response(request, user_id), media_type="text/event-stream"
    )
