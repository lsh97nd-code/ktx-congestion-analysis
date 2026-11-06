from unittest.mock import patch

import pandas as pd
import pytest

from backend import config
from backend.models.data import DataRecord, DataSummary
from backend.services import data_service
from backend.services.prompt_service import build_system_prompt
from scripts import analyze_data


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "ENV_FILE", tmp_path / ".env")
    monkeypatch.delenv("TREND_WINDOW_MONTHS", raising=False)


def series(values):
    dates = pd.date_range("2023-01-01", periods=len(values), freq="MS")
    records = [
        DataRecord(id=day.strftime("%Y-%m-%d"), date=day.strftime("%Y-%m-%d"), value=value, memo="월별 수요")
        for day, value in zip(dates, values)
    ]
    frame = pd.DataFrame({"date": dates, "monthly_boardings": values})
    return records, frame


def test_default_window_is_12_and_preserves_legacy_fields():
    assert config.get_trend_window_months() == 12
    records, frame = series([100] * 12 + [120] * 12)
    with patch.object(data_service, "list_data", return_value=records):
        summary = data_service.get_data_summary()
    assert summary.trend_window_months == 12
    assert summary.recent_window_avg == summary.recent_12_month_avg == 120
    assert summary.previous_window_avg == summary.previous_12_month_avg == 100
    offline = analyze_data.compute_recent_trend(frame)
    assert offline["trend_window_months"] == 12
    assert offline["recent_window_avg"] == offline["latest_12_month_avg"] == 120


def test_three_month_window_agrees_between_api_script_and_prompt(monkeypatch):
    monkeypatch.setenv("TREND_WINDOW_MONTHS", "3")
    records, frame = series([50, 100, 150, 120, 150, 180])
    with patch.object(data_service, "list_data", return_value=records):
        summary = data_service.get_data_summary()
    offline = analyze_data.compute_recent_trend(frame)
    assert summary.trend_window_months == offline["trend_window_months"] == 3
    assert summary.recent_window_avg == offline["recent_window_avg"] == 150
    assert summary.previous_window_avg == offline["previous_window_avg"] == 100
    assert summary.change_pct == offline["change_pct"] == 50
    assert summary.recent_12_month_avg is None
    assert summary.previous_12_month_avg is None
    assert offline["latest_12_month_avg"] is None
    assert offline["previous_12_month_avg"] is None
    prompt = build_system_prompt(summary)
    assert "최근 3개월 평균: 150.00명" in prompt
    assert "직전 3개월 평균: 100.00명" in prompt
    assert "최근 12개월" not in prompt
    assert "마지막 기록 월(2023-06)" in prompt
    assert "최근 30일을 뜻하지 않습니다" in prompt


def test_one_month_means_one_recorded_calendar_month(monkeypatch):
    monkeypatch.setenv("TREND_WINDOW_MONTHS", "1")
    records, frame = series([100, 150])
    with patch.object(data_service, "list_data", return_value=records):
        summary = data_service.get_data_summary()
    assert summary.recent_window_avg == 150
    assert summary.previous_window_avg == 100
    assert "최근 1개월" in analyze_data.compute_recent_trend(frame)["method"]


def test_custom_window_requires_twice_as_many_consecutive_months(monkeypatch):
    monkeypatch.setenv("TREND_WINDOW_MONTHS", "3")
    records, frame = series([100] * 5)
    with patch.object(data_service, "list_data", return_value=records):
        summary = data_service.get_data_summary()
    assert summary.trend_window_months == 3
    assert summary.recent_window_avg is None
    assert summary.trend == "데이터 부족"
    with pytest.raises(ValueError, match="최소 6개월"):
        analyze_data.compute_recent_trend(frame)

    records, frame = series([100] * 7)
    del records[3]
    with patch.object(data_service, "list_data", return_value=records):
        assert data_service.get_data_summary().trend == "데이터 부족"
    with pytest.raises(ValueError, match="누락"):
        analyze_data.compute_recent_trend(frame.drop(index=3))


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "abc", "", " ", "true"])
def test_invalid_window_is_rejected_before_reading_firestore(monkeypatch, value):
    monkeypatch.setenv("TREND_WINDOW_MONTHS", value)
    with patch.object(data_service, "list_data") as read:
        with pytest.raises(ValueError, match="TREND_WINDOW_MONTHS"):
            data_service.get_data_summary()
    read.assert_not_called()
    with pytest.raises(ValueError, match="TREND_WINDOW_MONTHS"):
        analyze_data.compute_recent_trend(pd.DataFrame())


def test_project_env_is_used_but_deployment_environment_wins(monkeypatch):
    config.ENV_FILE.write_text("TREND_WINDOW_MONTHS=3\n", encoding="utf-8")
    assert config.get_trend_window_months() == 3
    monkeypatch.setenv("TREND_WINDOW_MONTHS", "6")
    assert config.get_trend_window_months() == 6


def test_prompt_legacy_fallback_does_not_override_explicit_null():
    values = dict(period_start="2022-01-01", period_end="2023-12-01", count=24,
                  average=100, max=100, min=100, recent_12_month_avg=100,
                  previous_12_month_avg=100, trend="유지")
    assert "최근 12개월 평균: 100.00명" in build_system_prompt(DataSummary(**values))
    values["recent_window_avg"] = None
    assert "최근 12개월 평균: 계산 불가명" in build_system_prompt(DataSummary(**values))
