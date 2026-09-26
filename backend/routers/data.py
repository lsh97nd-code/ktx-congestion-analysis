"""HTTP routes for the Firestore ``data`` collection."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Response, status

from backend.models.data import DataCreate, DataRecord, DataSummary, DataUpdate
from backend.services.data_service import (
    DataAlreadyExistsError,
    DataNotFoundError,
    create_data,
    delete_data,
    get_data_summary,
    list_data,
    update_data,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["Data"])


@router.get("", response_model=list[DataRecord])
def get_data_list() -> list[DataRecord]:
    """Return all Firestore data documents."""
    try:
        return list_data()
    except Exception as exc:
        logger.exception("Firestore data 목록 조회 실패")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터를 불러오지 못했습니다.",
        ) from exc


@router.get("/summary", response_model=DataSummary)
def get_summary() -> DataSummary:
    """Return a live summary calculated from Firestore."""
    try:
        return get_data_summary()
    except DataNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요약할 데이터가 없습니다.",
        ) from exc
    except Exception as exc:
        logger.exception("Firestore data Summary 계산 실패")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터 요약을 불러오지 못했습니다.",
        ) from exc


@router.post("", response_model=DataRecord, status_code=status.HTTP_201_CREATED)
def post_data(payload: DataCreate) -> DataRecord:
    """Create one time-series document."""
    try:
        return create_data(payload)
    except DataAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="같은 날짜의 데이터가 이미 존재합니다.",
        ) from exc
    except Exception as exc:
        logger.exception("Firestore data 생성 실패")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터를 저장하지 못했습니다.",
        ) from exc


@router.put("/{document_id}", response_model=DataRecord)
def put_data(document_id: str, payload: DataUpdate) -> DataRecord:
    """Update one existing document."""
    try:
        return update_data(document_id, payload)
    except DataNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수정할 데이터를 찾지 못했습니다.",
        ) from exc
    except Exception as exc:
        logger.exception("Firestore data 수정 실패")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터를 수정하지 못했습니다.",
        ) from exc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_data(document_id: str) -> Response:
    """Delete one existing document."""
    try:
        delete_data(document_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except DataNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 데이터를 찾지 못했습니다.",
        ) from exc
    except Exception as exc:
        logger.exception("Firestore data 삭제 실패")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="데이터를 삭제하지 못했습니다.",
        ) from exc
