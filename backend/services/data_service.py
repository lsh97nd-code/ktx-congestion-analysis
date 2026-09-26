"""Business logic for the Firestore ``data`` collection."""

from __future__ import annotations

from statistics import mean

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


def _collection():
    return get_firestore_client().collection(COLLECTION_NAME)


def _snapshot_to_record(snapshot) -> DataRecord:
    payload = snapshot.to_dict() or {}
    return DataRecord(
        id=snapshot.id,
        date=str(payload.get("date", snapshot.id)),
        value=int(payload["value"]),
        memo=str(payload.get("memo", "")),
    )


def list_data() -> list[DataRecord]:
    """Return every data document ordered by its ISO date string."""
    snapshots = _collection().order_by("date").stream()
    return [_snapshot_to_record(snapshot) for snapshot in snapshots]


def create_data(payload: DataCreate) -> DataRecord:
    """Create a new document using the ISO date as its Firestore document ID."""
    document_id = payload.date.isoformat()
    document_ref = _collection().document(document_id)
    snapshot = document_ref.get()

    if snapshot.exists:
        raise DataAlreadyExistsError(document_id)

    document = {
        "date": document_id,
        "value": payload.value,
        "memo": payload.memo,
    }
    document_ref.set(document)
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
    """Calculate the assignment summary from the current Firestore documents."""
    records = list_data()

    if not records:
        raise DataNotFoundError("data collection is empty")

    values = [record.value for record in records]

    recent_avg: float | None = None
    previous_avg: float | None = None
    change_pct: float | None = None
    trend = "데이터 부족"

    if len(records) >= MIN_TREND_MONTHS:
        recent_values = values[-TREND_WINDOW_MONTHS:]
        previous_values = values[-MIN_TREND_MONTHS:-TREND_WINDOW_MONTHS]

        recent_avg = round(mean(recent_values), 2)
        previous_avg = round(mean(previous_values), 2)
        change_pct = _calculate_pct_change(previous_avg, recent_avg)

        if change_pct is None:
            trend = "유지"
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
