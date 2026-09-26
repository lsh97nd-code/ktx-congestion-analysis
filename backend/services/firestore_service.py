"""Firebase Firestore connection service.

Local development:
- Prefer GOOGLE_APPLICATION_CREDENTIALS pointing to the ignored service-account JSON.

Deployment:
- FIREBASE_SERVICE_ACCOUNT_JSON can contain the service-account JSON string.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.client import Client


def _initialize_firebase_app() -> firebase_admin.App:
    """Return the default Firebase app, initializing it only once."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()

        if service_account_json:
            try:
                service_account_info: dict[str, Any] = json.loads(service_account_json)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    "FIREBASE_SERVICE_ACCOUNT_JSON이 올바른 JSON 형식이 아닙니다."
                ) from exc

            credential = credentials.Certificate(service_account_info)
            return firebase_admin.initialize_app(credential)

        # Local development:
        # GOOGLE_APPLICATION_CREDENTIALS is resolved automatically by Firebase Admin.
        return firebase_admin.initialize_app()


@lru_cache(maxsize=1)
def get_firestore_client() -> Client:
    """Return a cached Firestore client."""
    app = _initialize_firebase_app()
    return firestore.client(app=app)


def check_firestore_connection() -> dict[str, str]:
    """Perform a lightweight Firestore connectivity check."""
    db = get_firestore_client()

    # Force one server request without depending on a specific document.
    list(db.collections())

    return {
        "status": "connected",
        "database": "firestore",
    }
