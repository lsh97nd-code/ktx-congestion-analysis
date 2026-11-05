from __future__ import annotations

import os
from functools import lru_cache

from openai import OpenAI

from backend.config import load_environment

DEFAULT_MODEL = "gpt-5.6-luna"
OPENAI_TIMEOUT_SECONDS = 30.0
OPENAI_MAX_RETRIES = 2


def _load_environment() -> None:
    """Load values from .env when the service is actually used."""
    load_environment()


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Create and reuse one OpenAI client."""
    _load_environment()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    return OpenAI(
        api_key=api_key,
        timeout=OPENAI_TIMEOUT_SECONDS,
        max_retries=OPENAI_MAX_RETRIES,
    )


def get_openai_model() -> str:
    """Return the model configured in the environment."""
    _load_environment()

    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip()
    return model or DEFAULT_MODEL


def generate_ai_response(user_message: str, system_prompt: str) -> str:
    """Generate one assistant response with the OpenAI Responses API."""
    user_message = user_message.strip()
    system_prompt = system_prompt.strip()

    if not user_message:
        raise ValueError("user_message는 비어 있을 수 없습니다.")
    if not system_prompt:
        raise ValueError("system_prompt는 비어 있을 수 없습니다.")

    response = get_openai_client().responses.create(
        model=get_openai_model(),
        instructions=system_prompt,
        input=user_message,
        store=False,
    )

    if response.status != "completed":
        raise RuntimeError("OpenAI 답변 생성이 완료되지 않았습니다.")

    answer = getattr(response, "output_text", None)
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("OpenAI 응답에서 텍스트를 확인할 수 없습니다.")

    return answer.strip()
