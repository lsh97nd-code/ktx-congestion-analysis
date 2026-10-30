"""One-time local integration test: Firestore summary -> system prompt -> OpenAI."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

# 이 파일을 `python .\scripts\test_openai_connection.py`로 직접 실행해도
# 프로젝트 루트의 backend 패키지를 찾을 수 있도록 경로를 추가합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 프로젝트 루트의 .env를 명시적으로 읽습니다.
load_dotenv(PROJECT_ROOT / ".env")

from backend.services.data_service import get_data_summary
from backend.services.openai_service import (
    OPENAI_TIMEOUT_SECONDS,
    generate_ai_response,
    get_openai_model,
)
from backend.services.prompt_service import build_system_prompt


def _format_change_pct(value: float | None) -> str:
    if value is None:
        return "계산 불가"
    return f"{value:.2f}%"


def main() -> None:
    summary = get_data_summary()
    system_prompt = build_system_prompt(summary)

    print("[1/4] Firestore Summary 읽기 완료")
    print(f"      기간: {summary.period_start} ~ {summary.period_end}")
    print(f"      데이터 수: {summary.count}")
    print(f"      추세: {summary.trend} / 변화율: {_format_change_pct(summary.change_pct)}")

    print("[2/4] System Prompt 구성 완료")
    print(f"[3/4] OpenAI 모델: {get_openai_model()}")
    print(
        "      실제 OpenAI API를 1회 호출합니다. "
        f"응답까지 최대 {OPENAI_TIMEOUT_SECONDS:g}초 정도 기다릴 수 있습니다."
    )

    answer = generate_ai_response(
        user_message="최근 KTX 월별 이용 수요 추세를 현재 데이터에 근거해서 간단히 설명해줘.",
        system_prompt=system_prompt,
    )

    print("[4/4] OpenAI 응답 수신 완료")
    print("\n--- AI 응답 ---")
    print(answer)


if __name__ == "__main__":
    main()
