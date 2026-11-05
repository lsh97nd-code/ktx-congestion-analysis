"""Load only this project's local configuration, never an ancestor's .env."""

from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


def load_environment() -> None:
    """Keep deployment environment variables authoritative over local defaults."""
    load_dotenv(ENV_FILE, override=False)
