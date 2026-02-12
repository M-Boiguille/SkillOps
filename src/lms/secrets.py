"""Secrets management helpers for SkillOps."""

from __future__ import annotations

import os
from typing import Iterable

SERVICE_NAME = "skillops"
DEFAULT_KEYS = (
    "GEMINI_API_KEY",
    "GITHUB_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "WAKATIME_API_KEY",
)


def _keyring_available() -> bool:
    try:
        import keyring  # noqa: F401

        return True
    except Exception:
        return False


def load_keyring_secrets(keys: Iterable[str] = DEFAULT_KEYS) -> None:
    """Load secrets from OS keyring into environment if missing.

    Enable with SKILLOPS_USE_KEYRING=true.
    """
    use_keyring = os.getenv("SKILLOPS_USE_KEYRING", "false").lower()
    if use_keyring not in {"1", "true", "yes"}:
        return
    if not _keyring_available():
        return

    import keyring

    for key in keys:
        if os.getenv(key):
            continue
        value = keyring.get_password(SERVICE_NAME, key)
        if value:
            os.environ[key] = value


def set_keyring_secret(key: str, value: str) -> None:
    """Store a secret in OS keyring."""
    if not _keyring_available():
        raise RuntimeError("keyring not available")
    import keyring

    keyring.set_password(SERVICE_NAME, key, value)


def delete_keyring_secret(key: str) -> None:
    """Delete a secret from OS keyring."""
    if not _keyring_available():
        raise RuntimeError("keyring not available")
    import keyring

    try:
        keyring.delete_password(SERVICE_NAME, key)
    except keyring.errors.PasswordDeleteError:
        pass
