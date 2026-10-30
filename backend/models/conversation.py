"""Pydantic models for conversation CRUD."""

from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

USER_MESSAGE_MAX_LENGTH = 4_000
ASSISTANT_MESSAGE_MAX_LENGTH = 12_000


class ConversationCreate(BaseModel):
    """Payload used to create a stored conversation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    user_message: str = Field(
        ...,
        min_length=1,
        max_length=USER_MESSAGE_MAX_LENGTH,
    )
    assistant_message: str = Field(
        ...,
        min_length=1,
        max_length=ASSISTANT_MESSAGE_MAX_LENGTH,
    )


class ConversationRecord(BaseModel):
    """Conversation document returned by the API."""

    id: str
    user_message: str
    assistant_message: str
    created_at: AwareDatetime
