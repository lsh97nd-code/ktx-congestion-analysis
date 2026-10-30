"""KTX Congestion Analysis FastAPI entry point."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.data import router as data_router
from backend.routers.conversations import router as conversations_router
from backend.routers.chat import router as chat_router


DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]


def get_allowed_origins() -> list[str]:
    """Return the configured CORS origins."""
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
app.include_router(conversations_router)
app.include_router(chat_router)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """API root endpoint."""
    return {"message": "KTX Congestion Analysis API", "status": "ok"}


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    """Process health endpoint."""
    return {"status": "healthy"}
