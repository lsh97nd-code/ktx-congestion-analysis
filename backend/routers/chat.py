from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.models.chat import ChatRequest, ChatResponse
from backend.services.chat_service import process_chat


router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def post_chat(payload: ChatRequest) -> ChatResponse:
    """Generate one AI answer using the current Firestore data summary."""
    try:
        result = process_chat(payload.message)
        return ChatResponse(**result)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
