import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from scripts import analyze_data, preprocess_data


@pytest.fixture(autouse=True)
def default_comparison_window(monkeypatch):
    monkeypatch.setenv("TREND_WINDOW_MONTHS", "12")


def monthly_frame(values):
    return pd.DataFrame(
        {"date": pd.date_range("2022-01-01", periods=len(values), freq="MS"),
         "monthly_boardings": values}
    )


@pytest.mark.parametrize("value", [None, "2024-1", "2024-01-02", "2024-13"])
def test_preprocessing_rejects_missing_or_non_month_dates(value):
    with pytest.raises(ValueError):
        preprocess_data.parse_month_column(pd.Series([value]), "운행년월")


@pytest.mark.parametrize("value", [None, -1, float("inf"), 1.5])
def test_preprocessing_rejects_invalid_counts(value):
    with pytest.raises(ValueError):
        preprocess_data.convert_numeric_columns(
            pd.DataFrame({"count": [value]}), ["count"], "input.csv", integer=True
        )


def test_hourly_averages_can_have_fractional_passengers():
    frame = pd.DataFrame({"count": [1.5]})
    preprocess_data.convert_numeric_columns(frame, ["count"], "input.csv")
    assert frame["count"].iloc[0] == 1.5


def test_missing_month_is_not_used_in_annual_or_month_over_month_comparison():
    frame = monthly_frame([100] * 25).drop(index=23)
    with pytest.raises(ValueError, match="누락"):
        analyze_data.compute_recent_trend(frame)
    with pytest.raises(ValueError, match="누락"):
        analyze_data.compute_monthly_total_summary(frame)


def test_analysis_represents_zero_baseline_as_undefined():
    summary = analyze_data.compute_recent_trend(monthly_frame([0] * 12 + [100] * 12))
    assert summary["change_pct"] is None
    assert summary["trend"] == "계산 불가"
    assert analyze_data.compute_monthly_total_summary(monthly_frame([0, 100]))["mom_change_pct"] is None


def test_analysis_sorts_months_before_comparison():
    frame = monthly_frame([100] * 12 + [120] * 12).iloc[::-1]
    assert analyze_data.compute_recent_trend(frame)["change_pct"] == 20
    assert analyze_data.compute_monthly_total_summary(frame)["latest_month"] == "2023-12-01"


def test_checked_in_data_retains_its_published_analysis():
    root = Path(__file__).resolve().parents[1]
    expected = json.loads((root / "data/processed/analysis_summary.json").read_text(encoding="utf-8"))
    actual, station_summary, firestore_monthly = analyze_data.analyze_ktx()
    expected.pop("rail_hourly_pattern", None)
    expected["recent_trend"].update(
        trend_window_months=12,
        recent_window_avg=expected["recent_trend"]["latest_12_month_avg"],
        previous_window_avg=expected["recent_trend"]["previous_12_month_avg"],
    )
    assert actual == expected
    assert len(firestore_monthly) == 168
    assert not station_summary.empty


@pytest.mark.parametrize("column,value", [("value", -1), ("value", 1.5), ("date", None), ("station", None)])
def test_analysis_rejects_corrupt_processed_rows(tmp_path, column, value):
    frame = pd.DataFrame({"date": ["2024-01-01"], "station": ["서울"], "direction": ["up"],
                          "boardings": [100], "alightings": [100], "value": [100], "memo": ["수요"]})
    frame[column] = value
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True)
    frame.to_csv(processed / "ktx_demand.csv", index=False, encoding="utf-8-sig")
    with patch.object(analyze_data, "PATHS", analyze_data.AnalysisPaths(tmp_path)):
        with pytest.raises(ValueError):
            analyze_data.load_ktx_data()
