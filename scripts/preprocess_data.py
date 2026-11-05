from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataPaths:
    """프로젝트 데이터 경로를 한 곳에서 관리한다."""

    root: Path = Path(__file__).resolve().parents[1]

    @property
    def raw_dir(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def ktx_file(self) -> Path:
        return self.raw_dir / "korail_ktx_station_monthly_2010_2023.csv"

    @property
    def hourly_file(self) -> Path:
        return self.raw_dir / "kotsa_rail_hourly_weekday_weekend_2025.csv"

    @property
    def ktx_out(self) -> Path:
        return self.processed_dir / "ktx_demand.csv"

    @property
    def hourly_out(self) -> Path:
        return self.processed_dir / "rail_hourly_pattern_2025.csv"


PATHS = DataPaths()

DIRECTION_MAP = {
    "down": {
        "label": "하행",
        "boardings": "하행_승차인원수",
        "alightings": "하행_하차인원수",
    },
    "up": {
        "label": "상행",
        "boardings": "상행_승차인원수",
        "alightings": "상행_하차인원수",
    },
}

DAY_TYPE_MAP = {
    "평일평균": "weekday_avg",
    "토요일": "saturday",
    "일요일": "sunday",
}


def setup_logging() -> None:
    """스크립트를 직접 실행할 때만 로깅 형식을 설정한다."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(message)s",
    )


def read_csv_korean(path: Path) -> pd.DataFrame:
    """공공데이터 CSV의 흔한 한글 인코딩을 순서대로 시도한다."""
    errors: list[str] = []

    for encoding in ("cp949", "utf-8-sig", "euc-kr", "utf-8"):
        try:
            df = pd.read_csv(path, encoding=encoding)
            logger.info("CSV 읽기 성공: %s (encoding=%s)", path.name, encoding)
            return df
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: {exc}")

    raise UnicodeError(
        f"CSV 인코딩을 읽지 못했습니다: {path}\n" + "\n".join(errors)
    )


def require_columns(
    df: pd.DataFrame,
    columns: set[str],
    file_name: str,
) -> None:
    """필수 컬럼이 모두 존재하는지 확인한다."""
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(
            f"{file_name}에 필요한 컬럼이 없습니다: {sorted(missing)}"
        )


def parse_month_column(series: pd.Series, column_name: str) -> pd.Series:
    """YYYY-MM 월 문자열을 날짜형으로 변환한다."""
    try:
        if series.isna().any() or not series.astype(str).str.fullmatch(r"\d{4}-\d{2}").all():
            raise ValueError("월 값이 없거나 YYYY-MM 형식이 아닙니다.")
        return pd.to_datetime(series, format="%Y-%m", errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"'{column_name}' 컬럼의 날짜 형식이 올바르지 않습니다. "
            "예상 형식: YYYY-MM"
        ) from exc


def convert_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
    file_name: str,
    *,
    integer: bool = False,
) -> None:
    """지정 컬럼을 숫자로 변환하고 문제 컬럼을 명확히 알려준다."""
    for column in columns:
        try:
            df[column] = pd.to_numeric(df[column], errors="raise")
            values = df[column]
            if values.isna().any() or not values.ge(0).all() or values.isin([float("inf"), float("-inf")]).any():
                raise ValueError("인원수는 유한한 0 이상의 숫자여야 합니다.")
            if integer and not values.mod(1).eq(0).all():
                raise ValueError("인원수는 정수여야 합니다.")
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"{file_name}의 '{column}' 컬럼에 "
                "유효하지 않은 인원수가 있습니다."
            ) from exc


def build_direction_rows(df: pd.DataFrame) -> pd.DataFrame:
    """상행/하행 Wide 데이터를 공통 Long Format으로 변환한다."""
    frames: list[pd.DataFrame] = []

    for direction, config in DIRECTION_MAP.items():
        frames.append(
            pd.DataFrame(
                {
                    "date": df["date"],
                    "station": df["정차역"].astype(str).str.strip(),
                    "direction": direction,
                    "boardings": df[config["boardings"]],
                    "alightings": df[config["alightings"]],
                }
            )
        )

    result = pd.concat(frames, ignore_index=True)
    result["value"] = result["boardings"]

    # 현재 벡터화 방식이 apply 기반 f-string보다 빠르므로 유지한다.
    # 과제의 기본 CRUD 구조가 (date, value, memo)이므로 memo도 유지한다.
    direction_labels = {
        direction: config["label"]
        for direction, config in DIRECTION_MAP.items()
    }
    result["memo"] = (
        result["station"]
        + " / "
        + result["direction"].map(direction_labels)
        + " / 월별 KTX 승차수요"
    )

    return result


def preprocess_ktx() -> pd.DataFrame:
    if not PATHS.ktx_file.exists():
        raise FileNotFoundError(
            "핵심 KTX 파일을 찾을 수 없습니다.\n"
            f"다음 위치에 파일을 두세요:\n{PATHS.ktx_file}"
        )

    df = read_csv_korean(PATHS.ktx_file)

    required = {
        "운행년월",
        "정차역",
        "하행_승차인원수",
        "하행_하차인원수",
        "상행_승차인원수",
        "상행_하차인원수",
    }
    require_columns(df, required, PATHS.ktx_file.name)
    if df.empty:
        raise ValueError("KTX 원본 데이터가 비어 있습니다.")
    if df["정차역"].isna().any() or df["정차역"].astype(str).str.strip().eq("").any():
        raise ValueError("KTX 원본 데이터에 정차역이 없는 행이 있습니다.")
    df["정차역"] = df["정차역"].astype(str).str.strip()

    logger.info(
        "KTX 원본 | 행=%s, 열=%s, 결측=%s, 완전중복=%s",
        f"{df.shape[0]:,}",
        df.shape[1],
        f"{int(df.isna().sum().sum()):,}",
        f"{int(df.duplicated().sum()):,}",
    )

    df["date"] = parse_month_column(df["운행년월"], "운행년월")
    if df.duplicated(["date", "정차역"]).any():
        raise ValueError("KTX 원본 데이터에 같은 월·정차역의 중복 행이 있습니다.")

    number_cols = [
        "하행_승차인원수",
        "하행_하차인원수",
        "상행_승차인원수",
        "상행_하차인원수",
    ]
    convert_numeric_columns(df, number_cols, PATHS.ktx_file.name, integer=True)

    result = build_direction_rows(df)
    result = result.sort_values(
        ["date", "station", "direction"],
        kind="stable",
    ).reset_index(drop=True)

    result["date"] = result["date"].dt.strftime("%Y-%m-%d")

    PATHS.processed_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(PATHS.ktx_out, index=False, encoding="utf-8-sig")

    logger.info("KTX 가공 저장: %s", PATHS.ktx_out)
    logger.info(
        "KTX 가공 결과 | 행=%s, 열=%s, 기간=%s~%s, 역=%s개",
        f"{result.shape[0]:,}",
        result.shape[1],
        result["date"].min(),
        result["date"].max(),
        result["station"].nunique(),
    )
    logger.info(
        "KTX value 통계 | 평균=%.2f, 최대=%s, 최소=%s",
        result["value"].mean(),
        f"{result['value'].max():,}",
        f"{result['value'].min():,}",
    )

    return result


def preprocess_hourly_pattern() -> pd.DataFrame | None:
    """철도 전체 시간대 패턴 보조 데이터를 Long Format으로 변환한다."""
    if not PATHS.hourly_file.exists():
        logger.warning(
            "시간대 보조파일이 없어 건너뜁니다: %s",
            PATHS.hourly_file.name,
        )
        return None

    df = read_csv_korean(PATHS.hourly_file)
    required = {"구분1", "평일평균", "토요일", "일요일"}
    require_columns(df, required, PATHS.hourly_file.name)

    convert_numeric_columns(
        df,
        ["평일평균", "토요일", "일요일"],
        PATHS.hourly_file.name,
    )

    result = df.melt(
        id_vars=["구분1"],
        value_vars=list(DAY_TYPE_MAP.keys()),
        var_name="day_type",
        value_name="passengers",
    ).rename(columns={"구분1": "hour_slot"})

    result["day_type"] = result["day_type"].map(DAY_TYPE_MAP)

    PATHS.processed_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(
        PATHS.hourly_out,
        index=False,
        encoding="utf-8-sig",
    )

    logger.info("시간대 보조 가공 저장: %s", PATHS.hourly_out)
    logger.info(
        "시간대 보조 결과 | 행=%s, 열=%s",
        f"{result.shape[0]:,}",
        result.shape[1],
    )
    logger.info(
        "주의: 시간대 보조자료는 KTX 전용이 아니라 "
        "철도 시간대 패턴 보조지표입니다."
    )

    return result


def main() -> None:
    setup_logging()
    preprocess_ktx()
    preprocess_hourly_pattern()
    logger.info("전처리가 완료되었습니다.")


if __name__ == "__main__":
    main()
