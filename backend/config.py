"""Load only this project's local configuration, never an ancestor's .env."""

import os
import re
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_TREND_WINDOW_MONTHS = 12


def load_environment() -> None:
    """Keep deployment environment variables authoritative over local defaults."""
    load_dotenv(ENV_FILE, override=False)


def get_trend_window_months() -> int:
    """Return the number of calendar months in each adjacent comparison window."""
    load_environment()
    raw = os.getenv("TREND_WINDOW_MONTHS", str(DEFAULT_TREND_WINDOW_MONTHS)).strip()
    if not re.fullmatch(r"[0-9]+", raw) or int(raw) < 1:
        raise ValueError("TREND_WINDOW_MONTHS는 1 이상의 정수여야 합니다.")
    return int(raw)
