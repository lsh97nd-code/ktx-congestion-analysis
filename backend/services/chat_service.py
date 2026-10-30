from __future__ import annotations

import logging
from typing import Any

from backend.services.conversation_service import create_conversation
from backend.services.data_service import get_data_summary
from backend.services.openai_service import generate_ai_response, get_openai_model
from backend.services.prompt_service import build_system_prompt


logger = logging.getLogger(__name__)


def _to_dict(record: Any) -> dict[str, Any]:
    """Normalize a service result to a plain dictionary."""
    if isinstance(record, dict):
        return record

    model_dump = getattr(record, "model_dump", None)
    if callable(model_dump):
        return model_dump()

    raise TypeError("대화 저장 결과를 dict 형태로 변환할 수 없습니다.")


def process_chat(message: str) -> dict[str, str]:
    """Build a live Firestore summary, ask OpenAI, and store the conversation."""
    try:
        summary = get_data_summary()
        system_prompt = build_system_prompt(summary)

        answer = generate_ai_response(
            user_message=message,
            system_prompt=system_prompt,
        )

        saved = _to_dict(
            create_conversation(
                {
                    "user_message": message,
                    "assistant_message": answer,
                }
            )
        )

        conversation_id = str(saved.get("id", "")).strip()
        if not conversation_id:
            raise RuntimeError(
                "Firestore 대화 저장 후 conversation_id를 확인할 수 없습니다."
            )

        return {
            "answer": answer,
            "conversation_id": conversation_id,
            "model": get_openai_model(),
        }

    except Exception as exc:
        logger.exception("Chat 처리 중 오류가 발생했습니다.")
        raise RuntimeError(
            "AI 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요."
        ) from exc
