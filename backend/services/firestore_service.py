from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client

from backend.config import PROJECT_ROOT, load_environment

logger = logging.getLogger(__name__)

LOCAL_SERVICE_ACCOUNT = PROJECT_ROOT / "secrets" / "firebase-service-account.json"

# 로컬 개발에서는 프로젝트 루트의 .env를 명시적으로 로드합니다.
# Render 등 배포 환경에서는 플랫폼 환경변수를 그대로 사용합니다.
load_environment()

_lock = threading.Lock()
_client: Client | None = None


def _get_existing_app() -> firebase_admin.App | None:
    """이미 초기화된 Firebase 앱이 있으면 반환합니다."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        return None


def _initialize_firebase_app() -> firebase_admin.App:
    """Firebase Admin SDK 앱을 인증정보 우선순위에 따라 초기화합니다."""
    existing_app = _get_existing_app()
    if existing_app is not None:
        return existing_app

    # 1. 배포 환경(Render 등): 서비스 계정 JSON 전체를 환경변수로 저장
    service_account_json = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_JSON", ""
    ).strip()

    if service_account_json:
        try:
            service_account_info = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON 형식이 올바른 JSON이 아닙니다."
            ) from exc

        credential = credentials.Certificate(service_account_info)
        logger.info("Firebase를 FIREBASE_SERVICE_ACCOUNT_JSON으로 초기화합니다.")
        return firebase_admin.initialize_app(credential)

    # 2. 로컬 개발: .env의 GOOGLE_APPLICATION_CREDENTIALS 경로 사용
    credentials_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", ""
    ).strip()

    if credentials_path:
        path = Path(credentials_path)

        if not path.is_absolute():
            path = PROJECT_ROOT / path

        if not path.exists():
            raise RuntimeError(
                f"Firebase 서비스 계정 파일을 찾을 수 없습니다: {path}"
            )

        credential = credentials.Certificate(str(path))
        logger.info(
            "Firebase를 GOOGLE_APPLICATION_CREDENTIALS 파일로 초기화합니다."
        )
        return firebase_admin.initialize_app(credential)

    # 3. 현재 프로젝트의 로컬 기본 위치
    if LOCAL_SERVICE_ACCOUNT.exists():
        credential = credentials.Certificate(str(LOCAL_SERVICE_ACCOUNT))
        logger.info(
            "Firebase를 로컬 기본 서비스 계정 파일로 초기화합니다: %s",
            LOCAL_SERVICE_ACCOUNT,
        )
        return firebase_admin.initialize_app(credential)

    # 인증정보 없이 ADC로 넘어가면 원인이 모호해질 수 있으므로 명확히 중단합니다.
    raise RuntimeError(
        "Firebase 인증정보를 찾을 수 없습니다. "
        "GOOGLE_APPLICATION_CREDENTIALS 또는 "
        "FIREBASE_SERVICE_ACCOUNT_JSON을 설정하거나 "
        "secrets/firebase-service-account.json 파일을 확인하세요."
    )


def get_firestore_client() -> Client:
    """Firestore 클라이언트를 최초 1회 생성한 뒤 재사용합니다."""
    global _client

    if _client is not None:
        return _client

    with _lock:
        if _client is None:
            app = _initialize_firebase_app()
            _client = firestore.client(app=app)
            logger.info("Firestore 클라이언트 초기화 완료")

    return _client
