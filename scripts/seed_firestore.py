"""Firestore 초기 데이터 업로드 스크립트.

data/processed/monthly_summary.csv의 date/value/memo를 검증한 뒤
Firestore `data` 컬렉션에 업로드합니다.

특징:
- 날짜를 Document ID로 사용해 재실행 시 중복 문서가 늘어나지 않음
- Firestore Batch Write를 400건 단위로 분할
- 업로드 후 대상 Document ID와 필드값을 다시 읽어 검증
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import firebase_admin
import pandas as pd
from firebase_admin import firestore
from google.cloud.firestore_v1.client import Client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "data" / "processed" / "monthly_summary.csv"

COLLECTION_NAME = "data"

# 과제 요구사항: 최소 100개 이상의 시계열 데이터
MIN_REQUIRED_ROWS = 100

# Firestore Batch Write 상한보다 여유 있게 설정
BATCH_SIZE = 400

EXPECTED_COLUMNS = {"date", "value", "memo"}

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(message)s",
    )


def load_seed_data(csv_path: Path) -> pd.DataFrame:
    """CSV를 읽고 Firestore 업로드 전 필수 조건을 검증합니다."""
    if not csv_path.exists():
        raise FileNotFoundError(f"입력 CSV를 찾을 수 없습니다: {csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    missing_columns = EXPECTED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"필수 컬럼이 없습니다: {sorted(missing_columns)}")

    df = df[["date", "value", "memo"]].copy()

    if df.empty:
        raise ValueError("업로드할 데이터가 없습니다.")

    if len(df) < MIN_REQUIRED_ROWS:
        raise ValueError(
            f"과제 최소 데이터 수({MIN_REQUIRED_ROWS})보다 적습니다: {len(df)}"
        )

    if df.isna().any().any():
        raise ValueError("date/value/memo에 결측치가 있습니다.")

    parsed_dates = pd.to_datetime(
        df["date"],
        format="%Y-%m-%d",
        errors="raise",
    )
    df["date"] = parsed_dates.dt.strftime("%Y-%m-%d")

    df["value"] = pd.to_numeric(df["value"], errors="raise")
    if ((df["value"] % 1) != 0).any():
        raise ValueError("value에는 정수형 승차인원만 허용합니다.")
    df["value"] = df["value"].astype("int64")

    df["memo"] = df["memo"].astype(str).str.strip()
    if (df["memo"] == "").any():
        raise ValueError("memo에 빈 문자열이 있습니다.")

    if df["date"].duplicated().any():
        duplicates = df.loc[df["date"].duplicated(), "date"].tolist()
        raise ValueError(f"중복 date가 있습니다: {duplicates[:5]}")

    df = df.sort_values("date").reset_index(drop=True)

    logger.info(
        "Seed 데이터 검증 완료 | rows=%s, first=%s, last=%s",
        len(df),
        df.iloc[0]["date"],
        df.iloc[-1]["date"],
    )
    return df


def get_firestore_client() -> Client:
    """Firebase Admin SDK를 안전하게 초기화하고 Firestore Client를 반환합니다."""
    credential_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credential_path:
        raise EnvironmentError(
            "GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다."
        )

    if not Path(credential_path).exists():
        raise FileNotFoundError(
            "GOOGLE_APPLICATION_CREDENTIALS가 가리키는 파일을 찾을 수 없습니다."
        )

    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app()

    return firestore.client()


def upload_data(db: Client, df: pd.DataFrame) -> int:
    """데이터를 BATCH_SIZE 단위로 나누어 Firestore에 업로드합니다."""
    total = 0

    for chunk_start in range(0, len(df), BATCH_SIZE):
        chunk = df.iloc[chunk_start : chunk_start + BATCH_SIZE]
        batch = db.batch()

        for row in chunk.itertuples(index=False):
            doc_ref = db.collection(COLLECTION_NAME).document(row.date)
            batch.set(
                doc_ref,
                {
                    "date": row.date,
                    "value": int(row.value),
                    "memo": row.memo,
                },
            )

        batch.commit()
        total += len(chunk)

        logger.info(
            "Batch 업로드 완료 | %s / %s",
            total,
            len(df),
        )

    logger.info(
        "Firestore 업로드 완료 | collection=%s, writes=%s",
        COLLECTION_NAME,
        total,
    )
    return total


def verify_upload(db: Client, df: pd.DataFrame) -> None:
    """이번 Seed 대상 Document ID와 핵심 필드값을 다시 읽어 검증합니다."""
    expected = {
        row.date: {
            "date": row.date,
            "value": int(row.value),
            "memo": row.memo,
        }
        for row in df.itertuples(index=False)
    }

    doc_refs = [
        db.collection(COLLECTION_NAME).document(doc_id)
        for doc_id in expected
    ]

    missing: list[str] = []
    mismatched: list[str] = []
    verified_count = 0

    for snapshot in db.get_all(doc_refs):
        doc_id = snapshot.id

        if not snapshot.exists:
            missing.append(doc_id)
            continue

        actual = snapshot.to_dict() or {}
        expected_doc = expected[doc_id]

        if any(
            actual.get(field) != expected_doc[field]
            for field in ("date", "value", "memo")
        ):
            mismatched.append(doc_id)
            continue

        verified_count += 1

    if missing:
        raise RuntimeError(
            "Firestore 검증 실패 - 누락 문서: "
            + ", ".join(missing[:10])
        )

    if mismatched:
        raise RuntimeError(
            "Firestore 검증 실패 - 값 불일치 문서: "
            + ", ".join(mismatched[:10])
        )

    if verified_count != len(expected):
        raise RuntimeError(
            f"Firestore 검증 실패: 예상 {len(expected)}건, 검증 {verified_count}건"
        )

    logger.info(
        "Firestore 검증 성공 | collection=%s, target_documents=%s",
        COLLECTION_NAME,
        verified_count,
    )


def main() -> None:
    setup_logging()

    df = load_seed_data(INPUT_CSV)
    db = get_firestore_client()

    uploaded = upload_data(db, df)

    if uploaded != len(df):
        raise RuntimeError(
            f"업로드 건수 불일치: 예상 {len(df)}건, 처리 {uploaded}건"
        )

    verify_upload(db, df)
    logger.info("Seed 작업 완료")


if __name__ == "__main__":
    main()
