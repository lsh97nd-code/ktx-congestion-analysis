"""Offline regressions for recent-history bounds and conversation API failures."""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers import conversations as routes
from backend.services import conversation_service as service


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(routes.router)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def record():
    return {
        "id": "conversation-1",
        "user_message": "최근 수요는?",
        "assistant_message": "월별 데이터를 확인해 주세요.",
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }


@pytest.mark.parametrize("query,expected", [("", 20), ("?limit=1", 1), ("?limit=100", 100)])
def test_list_forwards_bounded_limit(client, monkeypatch, record, query, expected):
    listing = Mock(return_value=[record])
    monkeypatch.setattr(routes, "list_conversations", listing)

    response = client.get(f"/api/conversations{query}")

    assert response.status_code == 200
    assert response.json()[0]["id"] == record["id"]
    listing.assert_called_once_with(limit=expected)


@pytest.mark.parametrize("limit", ["0", "-1", "101", "1.5", "invalid"])
def test_invalid_limit_does_not_query_database(client, monkeypatch, limit):
    listing = Mock()
    monkeypatch.setattr(routes, "list_conversations", listing)

    response = client.get(f"/api/conversations?limit={limit}")

    assert response.status_code == 422
    listing.assert_not_called()


@pytest.mark.parametrize(
    "method,path,service_name,payload",
    [
        ("get", "/api/conversations", "list_conversations", None),
        ("get", "/api/conversations/conversation-1", "get_conversation", None),
        ("delete", "/api/conversations/conversation-1", "delete_conversation", None),
        (
            "post", "/api/conversations", "create_conversation",
            {"user_message": "question", "assistant_message": "answer"},
        ),
    ],
)
def test_backend_errors_are_sanitized(client, monkeypatch, method, path, service_name, payload):
    monkeypatch.setattr(
        routes, service_name, Mock(side_effect=RuntimeError("private credential path"))
    )

    response = client.request(method, path, json=payload)

    assert response.status_code == 503
    assert "private credential" not in response.text
    assert "대화 요청을 처리하지 못했습니다" in response.json()["detail"]


@pytest.mark.parametrize("method,service_name,result", [
    ("get", "get_conversation", None),
    ("delete", "delete_conversation", False),
])
def test_missing_conversation_remains_404(client, monkeypatch, method, service_name, result):
    monkeypatch.setattr(routes, service_name, Mock(return_value=result))
    response = client.request(method, "/api/conversations/missing")
    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."


def test_malformed_stored_conversation_is_service_error(client, monkeypatch, record):
    record["created_at"] = "invalid timestamp"
    monkeypatch.setattr(routes, "get_conversation", Mock(return_value=record))
    response = client.get("/api/conversations/conversation-1")
    assert response.status_code == 503


def test_create_and_delete_success(client, monkeypatch, record):
    monkeypatch.setattr(routes, "create_conversation", Mock(return_value=record))
    monkeypatch.setattr(routes, "delete_conversation", Mock(return_value=True))
    response = client.post("/api/conversations", json={
        "user_message": record["user_message"],
        "assistant_message": record["assistant_message"],
    })
    assert response.status_code == 201
    assert response.json()["id"] == record["id"]
    deleted = client.delete("/api/conversations/conversation-1")
    assert deleted.status_code == 204
    assert deleted.content == b""


def test_firestore_limit_applies_before_streaming(monkeypatch, record):
    snapshot = Mock(id=record["id"])
    snapshot.to_dict.return_value = record
    db = Mock()
    query = db.collection.return_value.order_by.return_value
    query.limit.return_value.stream.return_value = [snapshot]
    monkeypatch.setattr(service, "get_firestore_client", Mock(return_value=db))

    assert service.list_conversations(limit=7) == [record]

    db.collection.assert_called_once_with("conversations")
    db.collection.return_value.order_by.assert_called_once_with(
        "created_at", direction=service.firestore.Query.DESCENDING
    )
    query.limit.assert_called_once_with(7)
    query.limit.return_value.stream.assert_called_once_with()
    query.stream.assert_not_called()


@pytest.mark.parametrize("limit", [0, -1, 101, 1.5, True, "20"])
def test_service_rejects_unbounded_limit_before_connecting(monkeypatch, limit):
    connect = Mock()
    monkeypatch.setattr(service, "get_firestore_client", connect)
    with pytest.raises(ValueError):
        service.list_conversations(limit=limit)
    connect.assert_not_called()
