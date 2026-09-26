"""KTX Congestion Analysis FastAPI entry point."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.data import router as data_router


DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]


def get_allowed_origins() -> list[str]:
    """ALLOWED_ORIGINS 환경변수를 쉼표로 분리해 CORS 허용 목록을 반환합니다."""
    raw = os.getenv("ALLOWED_ORIGINS", "")
    if not raw.strip():
        return DEFAULT_ORIGINS

    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(
    title="KTX Congestion Analysis API",
    description="KTX 수요 분석 및 AI 비서 Backend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """API 기본 동작 확인용 엔드포인트."""
    return {
        "message": "KTX Congestion Analysis API",
        "status": "ok",
    }


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    """FastAPI 프로세스 상태 확인용 엔드포인트."""
    return {"status": "healthy"}
