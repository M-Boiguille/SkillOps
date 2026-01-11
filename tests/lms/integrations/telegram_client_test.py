from types import SimpleNamespace

import pytest

from src.lms.integrations.telegram_client import TelegramClient


def test_from_env_requires_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    with pytest.raises(ValueError):
        TelegramClient.from_env()


def test_send_message_success(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")

    client = TelegramClient.from_env()

    def fake_post(url, json, timeout):
        assert "sendMessage" in url
        assert json["chat_id"] == "123"
        assert json["text"] == "hello"
        return SimpleNamespace(status_code=200, json=lambda: {"ok": True})

    monkeypatch.setattr("requests.post", fake_post)

    assert client.send_message("hello") is True


def test_test_connection_success(monkeypatch):
    client = TelegramClient(token="abc", chat_id="1")

    def fake_get(url, timeout):
        assert "getMe" in url
        return SimpleNamespace(status_code=200, json=lambda: {"ok": True})

    monkeypatch.setattr("requests.get", fake_get)

    assert client.test_connection() is True
