"""Integration tests for TelegramClient using Telegram Bot API.

These tests are skipped unless the following environment variables are set:
- TELEGRAM_BOT_TOKEN_INTEGRATION
- TELEGRAM_CHAT_ID_INTEGRATION

We keep tests minimal to avoid excessive messages. They verify:
1) getMe responds ok (token valid)
2) sendMessage succeeds to the provided chat
"""

from __future__ import annotations

import os
import uuid

import pytest

from src.lms.integrations.telegram_client import TelegramClient

REQUIRED_ENVS = ["TELEGRAM_BOT_TOKEN_INTEGRATION", "TELEGRAM_CHAT_ID_INTEGRATION"]

pytestmark = pytest.mark.skipif(
    any(os.getenv(env) is None for env in REQUIRED_ENVS),
    reason=(
        "Integration credentials not provided; set TELEGRAM_BOT_TOKEN_INTEGRATION "
        "and TELEGRAM_CHAT_ID_INTEGRATION"
    ),
)


def _build_client() -> TelegramClient:
    token = os.environ["TELEGRAM_BOT_TOKEN_INTEGRATION"]
    chat_id = os.environ["TELEGRAM_CHAT_ID_INTEGRATION"]
    return TelegramClient(token=token, chat_id=chat_id)


def test_getme_returns_ok() -> None:
    """getMe should return ok=True for a valid token."""
    client = _build_client()
    assert client.test_connection() is True


def test_send_message_returns_ok() -> None:
    """sendMessage should return ok=True for a valid chat and token."""
    client = _build_client()
    message = f"SkillOps integration test {uuid.uuid4().hex[:8]}"
    assert client.send_message(message) is True
