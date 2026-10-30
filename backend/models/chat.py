from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Response body returned after an AI answer is generated and stored."""

    answer: str
    conversation_id: str
    model: str
