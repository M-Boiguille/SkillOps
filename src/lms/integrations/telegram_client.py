"""Telegram client wrapper for sending SkillOps notifications."""

from __future__ import annotations

import os
import requests


class TelegramClient:
    """Lightweight Telegram Bot API client.

    Handles basic messaging for daily notifications without pulling extra
    dependencies. Uses HTTP requests to call Telegram's sendMessage and getMe
    endpoints.
    """

    API_URL = "https://api.telegram.org"

    def __init__(self, token: str, chat_id: str):
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is required")
        self.token = token
        self.chat_id = chat_id

    @classmethod
    def from_env(cls) -> "TelegramClient":
        """Build a client from environment variables."""
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        return cls(token=token, chat_id=chat_id)

    def _build_url(self, method: str) -> str:
        return f"{self.API_URL}/bot{self.token}/{method}"

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send a simple text message.

        Args:
            text: Message content.
            parse_mode: Telegram parse mode (Markdown/HTML).
        Returns:
            True if Telegram API responded with ok=True.
        """
        url = self._build_url("sendMessage")
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code >= 400:
            response.raise_for_status()
        data = response.json()
        return bool(data.get("ok"))

    def test_connection(self) -> bool:
        """Call getMe to validate token."""
        url = self._build_url("getMe")
        response = requests.get(url, timeout=5)
        if response.status_code >= 400:
            response.raise_for_status()
        data = response.json()
        return bool(data.get("ok"))
