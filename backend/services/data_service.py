"""Business logic for the Firestore ``data`` collection."""

from __future__ import annotations

from statistics import mean

from google.api_core.exceptions import AlreadyExists
from pydantic import ValidationError

from backend.models.data import DataCreate, DataRecord, DataSummary, DataUpdate
from backend.services.firestore_service import get_firestore_client


COLLECTION_NAME = "data"
TREND_WINDOW_MONTHS = 12
MIN_TREND_MONTHS = TREND_WINDOW_MONTHS * 2
TREND_THRESHOLD_PCT = 3.0


class DataNotFoundError(Exception):
    """Raised when a requested Firestore document does not exist."""


class DataAlreadyExistsError(Exception):
    """Raised when a document with the same date ID already exists."""


class DataMalformedError(RuntimeError):
    """Raised when a Firestore data document has an invalid required field."""


def _collection():
    return get_firestore_client().collection(COLLECTION_NAME)


def _snapshot_to_record(snapshot) -> DataRecord:
    """Convert one Firestore snapshot into a validated DataRecord."""
    payload = snapshot.to_dict() or {}

    if "value" not in payload:
        raise DataMalformedError(
            f"Firestore 문서 '{snapshot.id}'에 필수 필드 'value'가 없습니다."
        )

    try:
        return DataRecord(
            id=snapshot.id,
            date=payload.get("date", snapshot.id),
            value=payload["value"],
            memo=payload.get("memo", ""),
        )
    except (TypeError, ValueError, ValidationError) as exc:
        raise DataMalformedError(
            f"Firestore 문서 '{snapshot.id}'의 월별 데이터 형식이 올바르지 않습니다."
        ) from exc


def list_data() -> list[DataRecord]:
    """Return every data document ordered by its ISO date string."""
    snapshots = _collection().order_by("date").stream()
    return [_snapshot_to_record(snapshot) for snapshot in snapshots]


def create_data(payload: DataCreate) -> DataRecord:
    """Create a new document using the ISO date as its Firestore document ID."""
    document_id = payload.date.isoformat()
    document_ref = _collection().document(document_id)
    document = {
        "date": document_id,
        "value": payload.value,
        "memo": payload.memo,
    }
    try:
        document_ref.create(document)
    except AlreadyExists as exc:
        raise DataAlreadyExistsError(document_id) from exc
    return DataRecord(id=document_id, **document)


def update_data(document_id: str, payload: DataUpdate) -> DataRecord:
    """Update value/memo while keeping the date-based document ID immutable."""
    document_ref = _collection().document(document_id)
    snapshot = document_ref.get()

    if not snapshot.exists:
        raise DataNotFoundError(document_id)

    changes = payload.model_dump(exclude_none=True)
    document_ref.update(changes)

    updated = document_ref.get()
    return _snapshot_to_record(updated)


def delete_data(document_id: str) -> None:
    """Delete one document after confirming that it exists."""
    document_ref = _collection().document(document_id)
    snapshot = document_ref.get()

    if not snapshot.exists:
        raise DataNotFoundError(document_id)

    document_ref.delete()


def _calculate_pct_change(previous: float, current: float) -> float | None:
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 2)


def get_data_summary() -> DataSummary:
    """Calculate the assignment summary from one current Firestore data read."""
    records = sorted(list_data(), key=lambda record: record.date)

    if not records:
        raise DataNotFoundError("data collection is empty")

    if len({record.date for record in records}) != len(records):
        raise DataMalformedError("같은 월의 데이터가 중복되어 있습니다.")

    values = [record.value for record in records]

    recent_avg: float | None = None
    previous_avg: float | None = None
    change_pct: float | None = None
    trend = "데이터 부족"

    recent_months = [
        int(record.date[:4]) * 12 + int(record.date[5:7])
        for record in records[-MIN_TREND_MONTHS:]
    ]
    complete_window = len(recent_months) == MIN_TREND_MONTHS and all(
        current - previous == 1
        for previous, current in zip(recent_months, recent_months[1:])
    )

    if complete_window:
        recent_values = values[-TREND_WINDOW_MONTHS:]
        previous_values = values[-MIN_TREND_MONTHS:-TREND_WINDOW_MONTHS]

        recent_mean = mean(recent_values)
        previous_mean = mean(previous_values)
        recent_avg = round(recent_mean, 2)
        previous_avg = round(previous_mean, 2)
        change_pct = _calculate_pct_change(previous_mean, recent_mean)

        if change_pct is None:
            trend = "계산 불가"
        elif change_pct >= TREND_THRESHOLD_PCT:
            trend = "증가"
        elif change_pct <= -TREND_THRESHOLD_PCT:
            trend = "감소"
        else:
            trend = "유지"

    return DataSummary(
        period_start=records[0].date,
        period_end=records[-1].date,
        count=len(records),
        average=round(mean(values), 2),
        max=max(values),
        min=min(values),
        recent_12_month_avg=recent_avg,
        previous_12_month_avg=previous_avg,
        change_pct=change_pct,
        trend=trend,
    )
