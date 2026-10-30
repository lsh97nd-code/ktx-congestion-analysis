"""FastAPI routes for conversation CRUD."""

from fastapi import APIRouter, HTTPException, Response, status

from backend.models.conversation import ConversationCreate, ConversationRecord
from backend.services.conversation_service import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
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

    record = create_conversation(payload.model_dump())
    return ConversationRecord.model_validate(record)


@router.get(
    "",
    response_model=list[ConversationRecord],
)
def get_conversations() -> list[ConversationRecord]:
    """Return stored conversations newest first."""

    return [
        ConversationRecord.model_validate(record)
        for record in list_conversations()
    ]


@router.get(
    "/{conversation_id}",
    response_model=ConversationRecord,
)
def get_conversation_by_id(conversation_id: str) -> ConversationRecord:
    """Return one stored conversation."""

    record = get_conversation(conversation_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return ConversationRecord.model_validate(record)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_conversation(conversation_id: str) -> Response:
    """Delete one stored conversation."""

    deleted = delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
