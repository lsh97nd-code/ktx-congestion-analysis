"""Pydantic models for the Firestore data collection."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator


class DataCreate(BaseModel):
    """Request body used when creating one time-series document."""

    date: date
    value: int = Field(ge=0, description="전국 KTX 월 총승차인원")
    memo: str = Field(min_length=1, max_length=200)

    @field_validator("memo")
    @classmethod
    def validate_memo(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("memo는 빈 문자열일 수 없습니다.")
        return cleaned


class DataUpdate(BaseModel):
    """Request body used when updating an existing document."""

    value: int | None = Field(default=None, ge=0)
    memo: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("memo")
    @classmethod
    def validate_optional_memo(cls, value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()
        if not cleaned:
            raise ValueError("memo는 빈 문자열일 수 없습니다.")
        return cleaned

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "DataUpdate":
        if self.value is None and self.memo is None:
            raise ValueError("수정할 value 또는 memo 중 하나 이상을 입력해야 합니다.")
        return self


class DataRecord(BaseModel):
    """One Firestore data document returned by the API."""

    id: str
    date: str
    value: int
    memo: str


class DataSummary(BaseModel):
    """Live summary calculated from the current Firestore data collection."""

    period_start: str
    period_end: str
    count: int
    average: float
    max: int
    min: int
    recent_12_month_avg: float | None = None
    previous_12_month_avg: float | None = None
    change_pct: float | None = None
    trend: str
