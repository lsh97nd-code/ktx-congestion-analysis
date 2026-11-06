from unittest.mock import Mock, patch

import pytest
from google.api_core.exceptions import AlreadyExists
from pydantic import ValidationError

from backend.models.data import DataCreate, DataRecord, DataUpdate
from backend.services import data_service


@pytest.fixture(autouse=True)
def default_comparison_window(monkeypatch):
    monkeypatch.setenv("TREND_WINDOW_MONTHS", "12")


def monthly_records(values, start_year=2022):
    return [
        DataRecord(
            id=f"{start_year + index // 12}-{index % 12 + 1:02d}-01",
            date=f"{start_year + index // 12}-{index % 12 + 1:02d}-01",
            value=value,
            memo="월별 승차인원",
        )
        for index, value in enumerate(values)
    ]


@pytest.mark.parametrize("value", [-1, 1.5, True, "100"])
def test_requests_reject_invalid_passenger_counts(value):
    with pytest.raises(ValidationError):
        DataCreate(date="2024-01-01", value=value, memo="월별 승차인원")
    with pytest.raises(ValidationError):
        DataUpdate(value=value)


def test_create_requires_month_start():
    with pytest.raises(ValidationError):
        DataCreate(date="2024-01-02", value=100, memo="월별 승차인원")


@pytest.mark.parametrize("value", [1.5, -1, True, float("inf"), "100"])
def test_stored_counts_are_rejected_without_silent_coercion(value):
    snapshot = Mock(id="2024-01-01")
    snapshot.to_dict.return_value = {"date": "2024-01-01", "value": value}
    with pytest.raises(data_service.DataMalformedError):
        data_service._snapshot_to_record(snapshot)


def test_create_is_atomic_when_another_writer_has_created_the_month():
    collection = Mock()
    document = collection.document.return_value
    document.create.side_effect = AlreadyExists("already created by another writer")
    payload = DataCreate(date="2024-01-01", value=100, memo="월별 승차인원")
    with patch.object(data_service, "_collection", return_value=collection):
        with pytest.raises(data_service.DataAlreadyExistsError):
            data_service.create_data(payload)
    document.create.assert_called_once_with(
        {"date": "2024-01-01", "value": 100, "memo": "월별 승차인원"}
    )
    document.set.assert_not_called()


def test_summary_uses_consecutive_calendar_months_and_sorted_dates():
    records = monthly_records([100] * 12 + [120] * 12)
    with patch.object(data_service, "list_data", return_value=list(reversed(records))):
        summary = data_service.get_data_summary()
    assert summary.period_start == "2022-01-01"
    assert summary.period_end == "2023-12-01"
    assert summary.recent_12_month_avg == 120
    assert summary.previous_12_month_avg == 100
    assert summary.change_pct == 20
    assert summary.trend == "증가"


def test_summary_does_not_call_24_sparse_records_24_months():
    records = monthly_records([100] * 25)
    del records[12]
    with patch.object(data_service, "list_data", return_value=records):
        summary = data_service.get_data_summary()
    assert summary.count == 24
    assert summary.trend == "데이터 부족"
    assert summary.change_pct is None
    assert summary.recent_12_month_avg is None


def test_zero_baseline_is_not_reported_as_unchanged():
    with patch.object(
        data_service, "list_data", return_value=monthly_records([0] * 12 + [100] * 12)
    ):
        summary = data_service.get_data_summary()
    assert summary.change_pct is None
    assert summary.trend == "계산 불가"


def test_duplicate_months_are_not_double_counted():
    records = monthly_records([100] * 24)
    with patch.object(data_service, "list_data", return_value=records + records[-1:]):
        with pytest.raises(data_service.DataMalformedError):
            data_service.get_data_summary()


def test_percentage_uses_unrounded_averages():
    with patch.object(
        data_service, "list_data", return_value=monthly_records([1] + [0] * 11 + [2] + [0] * 11)
    ):
        summary = data_service.get_data_summary()
    assert summary.change_pct == 100
