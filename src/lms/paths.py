"""Shared path helpers for SkillOps."""

from __future__ import annotations

import os
from pathlib import Path


def get_storage_path() -> Path:
    """Return absolute storage path from env or default to ./storage."""
    storage_path_str = os.getenv("STORAGE_PATH", "storage")
    return Path(storage_path_str).expanduser().absolute()
