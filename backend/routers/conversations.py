"""FastAPI routes for conversation CRUD."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from backend.models.conversation import ConversationCreate, ConversationRecord
from backend.services.conversation_service import (
    DEFAULT_CONVERSATION_LIMIT,
    MAX_CONVERSATION_LIMIT,
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
)

logger = logging.getLogger(__name__)


def _unavailable() -> HTTPException:
    """Expose a stable error without leaking database or credential details."""
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="대화 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.",
    )


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationRecord,
    status_code=status.HTTP_201_CREATED,
)
def post_conversation(payload: ConversationCreate) -> ConversationRecord:
    """Create one stored conversation."""

    try:
        record = create_conversation(payload.model_dump())
        return ConversationRecord.model_validate(record)
    except Exception as exc:
        logger.exception("Firestore 대화 저장 실패")
        raise _unavailable() from exc


@router.get(
    "",
    response_model=list[ConversationRecord],
)
def get_conversations(
    limit: Annotated[int, Query(ge=1, le=MAX_CONVERSATION_LIMIT)] = DEFAULT_CONVERSATION_LIMIT,
) -> list[ConversationRecord]:
    """Return the requested number of recent conversations, newest first."""

    try:
        return [
            ConversationRecord.model_validate(record)
            for record in list_conversations(limit=limit)
        ]
    except Exception as exc:
        logger.exception("Firestore 대화 목록 조회 실패")
        raise _unavailable() from exc


@router.get(
    "/{conversation_id}",
    response_model=ConversationRecord,
)
def get_conversation_by_id(conversation_id: str) -> ConversationRecord:
    """Return one stored conversation."""

    try:
        record = get_conversation(conversation_id)
        if record is not None:
            return ConversationRecord.model_validate(record)
    except Exception as exc:
        logger.exception("Firestore 대화 조회 실패")
        raise _unavailable() from exc

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_conversation(conversation_id: str) -> Response:
    """Delete one stored conversation."""

    try:
        deleted = delete_conversation(conversation_id)
    except Exception as exc:
        logger.exception("Firestore 대화 삭제 실패")
        raise _unavailable() from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
