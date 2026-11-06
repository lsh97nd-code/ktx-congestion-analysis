"""Build the system prompt from the current Firestore data summary."""

from __future__ import annotations

from backend.models.data import DataSummary


SYSTEM_ROLE = "당신은 KTX 수요 데이터를 설명하는 AI 비서입니다."


def _format_number(value: int | float | None) -> str:
    """Format numeric summary values for readable Korean prompt text."""
    if value is None:
        return "계산 불가"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return f"{value:,}"


def _format_percent(value: float | None) -> str:
    """Format a percentage without producing text such as '계산 불가%'."""
    if value is None:
        return "계산 불가"
    return f"{value:,.2f}%"


def build_system_prompt(summary: DataSummary) -> str:
    """Create a grounded system prompt from a live Firestore summary."""
    window_months = summary.trend_window_months
    recent_avg = summary.recent_window_avg
    previous_avg = summary.previous_window_avg
    # Old saved summaries omit the new keys. An explicit null still means unavailable.
    if window_months == 12:
        if "recent_window_avg" not in summary.model_fields_set:
            recent_avg = summary.recent_12_month_avg
        if "previous_window_avg" not in summary.model_fields_set:
            previous_avg = summary.previous_12_month_avg
    return f"""{SYSTEM_ROLE}

[현재 Firestore 데이터 요약]
- 분석 기간: {summary.period_start} ~ {summary.period_end}
- 데이터 수: {summary.count}건
- 월평균 승차인원: {_format_number(summary.average)}명
- 최댓값: {_format_number(summary.max)}명
- 최솟값: {_format_number(summary.min)}명
- 최근 {window_months}개월 평균: {_format_number(recent_avg)}명
- 직전 {window_months}개월 평균: {_format_number(previous_avg)}명
- 변화율: {_format_percent(summary.change_pct)}
- 추세: {summary.trend}

[데이터 의미]
- 이 데이터는 전국 KTX 월별 총 승차인원 시계열입니다.
- 최근/직전 비교는 오늘이 아니라 마지막 기록 월({summary.period_end[:7]})을 기준으로 한 각각 {window_months}개월입니다.
- 1개월은 해당 달의 월 집계이며 최근 30일을 뜻하지 않습니다. 최근 30일 분석에는 일별 데이터가 필요합니다.
- 월별 집계 데이터이므로 특정 요일이나 특정 시간대의 KTX 수요를 직접 보여주지는 않습니다.
- 실시간 잔여 좌석, 매진 여부, 매진 확률을 제공하는 데이터가 아닙니다.

[답변 원칙]
- 위 요약에 근거해 답하고, 데이터에 없는 사실은 추정값처럼 단정하지 않습니다.
- 특정 요일·시간대 질문에는 월별 데이터만으로 직접 판단할 수 없다는 한계를 함께 설명합니다.
- 실제 좌석 상황이나 매진 가능성을 묻는 경우, 현재 데이터만으로 확인할 수 없다고 분명히 안내합니다.
- 숫자를 설명할 때는 사용자가 이해하기 쉬운 한국어를 사용합니다.
- 답변은 핵심부터 간결하게 설명합니다.
""".strip()
