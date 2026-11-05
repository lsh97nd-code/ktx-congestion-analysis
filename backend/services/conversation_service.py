"""Firestore service for conversation CRUD."""

from typing import Any

from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from backend.services.firestore_service import get_firestore_client

COLLECTION_NAME = "conversations"
DEFAULT_CONVERSATION_LIMIT = 20
MAX_CONVERSATION_LIMIT = 100


def _snapshot_to_record(snapshot: DocumentSnapshot) -> dict[str, Any]:
    """Convert a Firestore document snapshot into an API-friendly dict."""

    data = snapshot.to_dict()
    if data is None:
        raise ValueError(f"Conversation document has no data: {snapshot.id}")

    user_message = data.get("user_message")
    assistant_message = data.get("assistant_message")
    created_at = data.get("created_at")

    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError(f"Invalid user_message in conversation: {snapshot.id}")
    if not isinstance(assistant_message, str) or not assistant_message.strip():
        raise ValueError(f"Invalid assistant_message in conversation: {snapshot.id}")
    if created_at is None:
        raise ValueError(f"Missing created_at in conversation: {snapshot.id}")

    return {
        "id": snapshot.id,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "created_at": created_at,
    }


def create_conversation(payload: dict[str, Any]) -> dict[str, Any]:
    """Create one conversation document and return the stored record."""

    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document()

    doc_ref.set(
        {
            "user_message": payload["user_message"],
            "assistant_message": payload["assistant_message"],
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )

    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise RuntimeError("Conversation was written but could not be read back.")

    return _snapshot_to_record(snapshot)


def list_conversations(
    limit: int = DEFAULT_CONVERSATION_LIMIT,
) -> list[dict[str, Any]]:
    """Return a bounded page of the newest conversations."""

    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_CONVERSATION_LIMIT:
        raise ValueError(f"limit must be an integer between 1 and {MAX_CONVERSATION_LIMIT}.")

    db = get_firestore_client()

    snapshots = (
        db.collection(COLLECTION_NAME)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    return [_snapshot_to_record(snapshot) for snapshot in snapshots]


def get_conversation(conversation_id: str) -> dict[str, Any] | None:
    """Return one conversation, or None when it does not exist."""

    db = get_firestore_client()
    snapshot = db.collection(COLLECTION_NAME).document(conversation_id).get()

    if not snapshot.exists:
        return None

    return _snapshot_to_record(snapshot)


def delete_conversation(conversation_id: str) -> bool:
    """Delete one conversation and report whether it existed."""

    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(conversation_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return False

    doc_ref.delete()
    return True
