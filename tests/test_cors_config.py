from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from backend.main import DEFAULT_ORIGINS, get_allowed_origins


def test_additional_origin_preserves_existing_allowlist(monkeypatch):
    render = "https://ktx-congestion-analysis-frontend.onrender.com"
    vercel = "https://ktx-congestion-analysis-frontend.vercel.app"
    monkeypatch.setenv("ALLOWED_ORIGINS", f"{render}, http://localhost:5500")
    monkeypatch.setenv("ADDITIONAL_ALLOWED_ORIGINS", f"{vercel}/, {render}")
    assert get_allowed_origins() == [render, "http://localhost:5500", vercel]

    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=get_allowed_origins(), allow_methods=["*"], allow_headers=["*"])
    with TestClient(app) as client:
        response = client.options("/api/chat", headers={"Origin": vercel, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"})
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == vercel
        denied = client.options("/api/chat", headers={"Origin": "https://unrelated.example", "Access-Control-Request-Method": "POST"})
        assert denied.status_code == 400
        assert "access-control-allow-origin" not in denied.headers


def test_empty_additional_origins_preserves_local_defaults(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("ADDITIONAL_ALLOWED_ORIGINS", raising=False)
    assert get_allowed_origins() == DEFAULT_ORIGINS
