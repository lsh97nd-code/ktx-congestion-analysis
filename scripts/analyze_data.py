from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import get_trend_window_months

logger = logging.getLogger(__name__)

TREND_THRESHOLD_PCT = 3.0


@dataclass(frozen=True)
class AnalysisPaths:
    """분석 입력/출력 경로를 한 곳에서 관리한다."""

    root: Path = Path(__file__).resolve().parents[1]

    @property
    def processed_dir(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def ktx_file(self) -> Path:
        return self.processed_dir / "ktx_demand.csv"

    @property
    def hourly_file(self) -> Path:
        return self.processed_dir / "rail_hourly_pattern_2025.csv"

    @property
    def summary_json(self) -> Path:
        return self.processed_dir / "analysis_summary.json"

    @property
    def station_summary_csv(self) -> Path:
        return self.processed_dir / "station_summary.csv"

    @property
    def monthly_summary_csv(self) -> Path:
        return self.processed_dir / "monthly_summary.csv"


PATHS = AnalysisPaths()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(message)s",
    )


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"필요한 가공 파일이 없습니다: {path}\n"
            "먼저 scripts/preprocess_data.py를 실행하세요."
        )


def require_columns(
    df: pd.DataFrame,
    columns: set[str],
    file_name: str,
) -> None:
    """필수 컬럼을 검사한다. 공통 utils 분리는 Backend 구축 시 함께 정리한다."""
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(
            f"{file_name}에 필요한 컬럼이 없습니다: {sorted(missing)}"
        )


def calculate_pct_change(current: float, previous: float) -> float | None:
    """0으로 나누는 오류 없이 증감률을 계산한다."""
    if previous == 0:
        return None
    return (current - previous) / previous * 100


def classify_trend(change_pct: float | None) -> str:
    if change_pct is None:
        return "계산 불가"
    if change_pct >= TREND_THRESHOLD_PCT:
        return "증가"
    if change_pct <= -TREND_THRESHOLD_PCT:
        return "감소"
    return "유지"


def load_ktx_data() -> pd.DataFrame:
    """전처리된 KTX 데이터를 읽고 필수 컬럼과 자료형을 검증한다."""
    require_file(PATHS.ktx_file)

    df = pd.read_csv(PATHS.ktx_file, encoding="utf-8-sig")
    required = {
        "date",
        "station",
        "direction",
        "boardings",
        "alightings",
        "value",
        "memo",
    }
    require_columns(df, required, PATHS.ktx_file.name)
    if df.empty:
        raise ValueError("KTX 가공 데이터가 비어 있습니다.")

    df["date"] = pd.to_datetime(df["date"], errors="raise")
    if df["date"].isna().any() or not df["date"].dt.is_month_start.all():
        raise ValueError("KTX 가공 데이터의 date는 각 월의 1일이어야 합니다.")
    if df["station"].isna().any() or df["station"].astype(str).str.strip().eq("").any():
        raise ValueError("KTX 가공 데이터에 정차역이 없는 행이 있습니다.")
    df["station"] = df["station"].astype(str).str.strip()
    if not df["direction"].isin(["up", "down"]).all():
        raise ValueError("KTX 가공 데이터의 direction은 up 또는 down이어야 합니다.")
    if df.duplicated(["date", "station", "direction"]).any():
        raise ValueError("KTX 가공 데이터에 같은 월·역·방향의 중복 행이 있습니다.")
    for column in ("boardings", "alightings", "value"):
        df[column] = pd.to_numeric(df[column], errors="raise")
        values = df[column]
        if values.isna().any() or not values.ge(0).all() or not values.mod(1).eq(0).all():
            raise ValueError(f"KTX 가공 데이터의 {column}은 0 이상의 정수여야 합니다.")
    if not df["value"].eq(df["boardings"]).all():
        raise ValueError("KTX 가공 데이터의 value는 boardings와 같아야 합니다.")

    return df


def build_monthly_total(df: pd.DataFrame) -> pd.DataFrame:
    """전국 KTX 월 총승차인원 시계열을 만든다."""
    return (
        df.groupby("date", as_index=False)["value"]
        .sum()
        .rename(columns={"value": "monthly_boardings"})
        .sort_values("date")
        .reset_index(drop=True)
    )


def compute_recent_trend(monthly: pd.DataFrame) -> dict:
    """설정된 N개월씩의 인접 구간에서 월평균 총승차인원을 비교한다."""
    window_months = get_trend_window_months()
    required_months = window_months * 2
    if len(monthly) < required_months:
        raise ValueError(
            f"최근 추세 비교를 위해 최소 {required_months}개월의 "
            "월별 데이터가 필요합니다."
        )

    monthly = monthly.sort_values("date").reset_index(drop=True)
    _require_consecutive_months(monthly.tail(required_months))
    latest_window = monthly.tail(window_months)
    previous_window = monthly.iloc[
        -required_months:-window_months
    ]

    latest_avg = float(latest_window["monthly_boardings"].mean())
    previous_avg = float(previous_window["monthly_boardings"].mean())
    change_pct = calculate_pct_change(latest_avg, previous_avg)

    return {
        "method": (
            f"최근 {window_months}개월 월평균 총승차인원 vs "
            f"직전 {window_months}개월 월평균 총승차인원"
        ),
        "threshold_pct": TREND_THRESHOLD_PCT,
        "trend_window_months": window_months,
        "recent_window_avg": round(latest_avg, 2),
        "previous_window_avg": round(previous_avg, 2),
        "latest_12_month_avg": round(latest_avg, 2) if window_months == 12 else None,
        "previous_12_month_avg": round(previous_avg, 2) if window_months == 12 else None,
        "change_pct": round(change_pct, 2) if change_pct is not None else None,
        "trend": classify_trend(change_pct),
    }


def _require_consecutive_months(monthly: pd.DataFrame) -> None:
    """누락 월이나 중복 월을 연속된 월로 오인하지 않도록 확인한다."""
    dates = pd.to_datetime(monthly["date"], errors="raise")
    if dates.isna().any() or not dates.dt.is_month_start.all():
        raise ValueError("월별 데이터의 날짜는 각 월의 1일이어야 합니다.")
    months = dates.dt.year * 12 + dates.dt.month
    if not months.diff().iloc[1:].eq(1).all():
        raise ValueError("비교 구간에 중복되거나 누락된 월이 있습니다.")


def compute_monthly_total_summary(monthly: pd.DataFrame) -> dict:
    """최신 월과 직전 월의 총승차인원 및 전월 대비 증감률을 계산한다."""
    if len(monthly) < 2:
        raise ValueError("전월 대비 계산을 위해 최소 2개월 데이터가 필요합니다.")

    monthly = monthly.sort_values("date").reset_index(drop=True)
    _require_consecutive_months(monthly.tail(2))
    latest = monthly.iloc[-1]
    previous = monthly.iloc[-2]

    mom_change_pct = calculate_pct_change(
        float(latest["monthly_boardings"]),
        float(previous["monthly_boardings"]),
    )

    return {
        "latest_month": latest["date"].strftime("%Y-%m-%d"),
        "latest_month_boardings": int(latest["monthly_boardings"]),
        "previous_month": previous["date"].strftime("%Y-%m-%d"),
        "previous_month_boardings": int(previous["monthly_boardings"]),
        "mom_change_pct": round(mom_change_pct, 2) if mom_change_pct is not None else None,
    }


def compute_station_summary(df: pd.DataFrame) -> pd.DataFrame:
    """역·방향별 장기 승차수요 통계를 만든다."""
    return (
        df.groupby(["station", "direction"], as_index=False)
        .agg(
            record_count=("value", "size"),
            average_boardings=("value", "mean"),
            max_boardings=("value", "max"),
            min_boardings=("value", "min"),
            total_boardings=("value", "sum"),
        )
        .sort_values(
            ["total_boardings", "station", "direction"],
            ascending=[False, True, True],
        )
        .reset_index(drop=True)
    )


def build_firestore_monthly_data(monthly: pd.DataFrame) -> pd.DataFrame:
    """Firestore data 컬렉션에 넣을 168개 월별 대표 시계열을 만든다."""
    result = monthly.rename(
        columns={"monthly_boardings": "value"}
    ).copy()
    result["date"] = result["date"].dt.strftime("%Y-%m-%d")
    result["memo"] = "전국 KTX 월 총승차인원"
    return result[["date", "value", "memo"]]


def build_analysis_summary(
    df: pd.DataFrame,
    monthly_total: dict,
    recent_trend: dict,
) -> dict:
    """API와 System Prompt에서 사용할 구조화 Summary를 생성한다."""
    return {
        "period": {
            "start": df["date"].min().strftime("%Y-%m-%d"),
            "end": df["date"].max().strftime("%Y-%m-%d"),
        },
        "record_count": int(len(df)),
        "station_count": int(df["station"].nunique()),
        "value_definition": "역·방향별 월 승차인원",
        "value_stats": {
            "average": round(float(df["value"].mean()), 2),
            "maximum": int(df["value"].max()),
            "minimum": int(df["value"].min()),
        },
        "monthly_total": monthly_total,
        "recent_trend": recent_trend,
    }


def analyze_ktx() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """KTX 분석 결과와 Firestore용 월별 데이터를 생성한다."""
    df = load_ktx_data()
    monthly = build_monthly_total(df)

    recent_trend = compute_recent_trend(monthly)
    monthly_total = compute_monthly_total_summary(monthly)
    station_summary = compute_station_summary(df)
    firestore_monthly = build_firestore_monthly_data(monthly)

    summary = build_analysis_summary(
        df=df,
        monthly_total=monthly_total,
        recent_trend=recent_trend,
    )

    return summary, station_summary, firestore_monthly


def analyze_hourly_pattern() -> dict | None:
    """철도 전체 시간대 보조지표의 요일유형별 최대 시간대를 계산한다."""
    if not PATHS.hourly_file.exists():
        logger.warning(
            "시간대 보조 가공파일이 없어 시간대 분석을 건너뜁니다: %s",
            PATHS.hourly_file.name,
        )
        return None

    df = pd.read_csv(PATHS.hourly_file, encoding="utf-8-sig")
    required = {"hour_slot", "day_type", "passengers"}
    require_columns(df, required, PATHS.hourly_file.name)

    df["passengers"] = pd.to_numeric(
        df["passengers"],
        errors="raise",
    )

    peaks: dict[str, dict] = {}
    for day_type, group in df.groupby("day_type"):
        peak_row = group.loc[group["passengers"].idxmax()]
        peaks[str(day_type)] = {
            "peak_hour_slot": str(peak_row["hour_slot"]),
            "peak_passengers": int(peak_row["passengers"]),
        }

    return {
        "note": (
            "KTX 전용 데이터가 아니라 철도 전체의 평일/토요일/일요일 "
            "시간대 패턴 보조지표"
        ),
        "peaks": peaks,
    }


def save_results(
    summary: dict,
    station_summary: pd.DataFrame,
    firestore_monthly: pd.DataFrame,
) -> None:
    """분석 결과 파일을 저장한다."""
    PATHS.processed_dir.mkdir(parents=True, exist_ok=True)

    with PATHS.summary_json.open("w", encoding="utf-8") as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2,
        )

    station_summary.to_csv(
        PATHS.station_summary_csv,
        index=False,
        encoding="utf-8-sig",
    )

    firestore_monthly.to_csv(
        PATHS.monthly_summary_csv,
        index=False,
        encoding="utf-8-sig",
    )


def main() -> None:
    setup_logging()

    summary, station_summary, firestore_monthly = analyze_ktx()
    hourly = analyze_hourly_pattern()

    if hourly is not None:
        summary["rail_hourly_pattern"] = hourly

    save_results(
        summary=summary,
        station_summary=station_summary,
        firestore_monthly=firestore_monthly,
    )

    logger.info("분석 Summary 저장: %s", PATHS.summary_json)
    logger.info("역별 Summary 저장: %s", PATHS.station_summary_csv)
    logger.info(
        "Firestore 월별 데이터 저장: %s",
        PATHS.monthly_summary_csv,
    )
    logger.info(
        "필수 Summary | 기간=%s~%s, 개수=%s, 평균=%.2f, "
        "최대=%s, 최소=%s, 최근추세=%s",
        summary["period"]["start"],
        summary["period"]["end"],
        f"{summary['record_count']:,}",
        summary["value_stats"]["average"],
        f"{summary['value_stats']['maximum']:,}",
        f"{summary['value_stats']['minimum']:,}",
        summary["recent_trend"]["trend"],
    )
    logger.info(
        "최근 추세 근거 | 최근%s개월 평균=%.2f, "
        "직전%s개월 평균=%.2f, 변화율=%s%%",
        summary["recent_trend"]["trend_window_months"],
        summary["recent_trend"]["recent_window_avg"],
        summary["recent_trend"]["trend_window_months"],
        summary["recent_trend"]["previous_window_avg"],
        summary["recent_trend"]["change_pct"],
    )
    logger.info(
        "Firestore data 컬렉션 후보 | %s개 월별 레코드",
        len(firestore_monthly),
    )


if __name__ == "__main__":
    main()
