"""AI configuration helpers for SkillOps."""

from __future__ import annotations

import os

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def get_gemini_model() -> str:
    """Return the configured Gemini model name."""
    return os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
