"""Offline API checks for baseline protection and error behavior."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import data as routes
from backend.services.data_service import DataAlreadyExistsError, DataNotFoundError


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize("method", ["post", "put", "delete"])
def test_seed_data_is_protected_before_database_access(client, monkeypatch, method):
    operation = Mock()
    monkeypatch.setattr(routes, {"post": "create_data", "put": "update_data", "delete": "delete_data"}[method], operation)
    url = "/api/data" if method == "post" else "/api/data/2023-12-01"
    kwargs = {} if method == "delete" else {"json": {"date": "2023-12-01", "value": 10, "memo": "test"}}
    response = client.request(method, url, **kwargs)
    assert response.status_code == 403
    operation.assert_not_called()


@pytest.mark.parametrize("document_id", ["invalid", "20240101", "2024-02-15"])
@pytest.mark.parametrize("method", ["put", "delete"])
def test_invalid_document_id_rejected(client, monkeypatch, document_id, method):
    operation = Mock()
    monkeypatch.setattr(routes, "update_data" if method == "put" else "delete_data", operation)
    kwargs = {"json": {"value": 1}} if method == "put" else {}
    assert client.request(method, f"/api/data/{document_id}", **kwargs).status_code == 422
    operation.assert_not_called()


def test_demo_data_can_still_be_created(client, monkeypatch):
    payload = {"date": "2024-01-01", "value": 7000000, "memo": "test"}
    operation = Mock(return_value={"id": payload["date"], **payload})
    monkeypatch.setattr(routes, "create_data", operation)
    response = client.post("/api/data", json=payload)
    assert response.status_code == 201
    assert response.json()["value"] == payload["value"]
    operation.assert_called_once()


@pytest.mark.parametrize("error,expected", [(DataAlreadyExistsError(), 409), (RuntimeError("private credential path"), 503)])
def test_create_errors_remain_sanitized(client, monkeypatch, error, expected):
    monkeypatch.setattr(routes, "create_data", Mock(side_effect=error))
    response = client.post("/api/data", json={"date": "2024-01-01", "value": 1, "memo": "test"})
    assert response.status_code == expected
    assert "private credential" not in response.text


def test_missing_demo_data_remains_404(client, monkeypatch):
    monkeypatch.setattr(routes, "delete_data", Mock(side_effect=DataNotFoundError()))
    assert client.delete("/api/data/2024-01-01").status_code == 404


def test_health_does_not_need_credentials(client):
    assert client.get("/health").json() == {"status": "healthy"}
