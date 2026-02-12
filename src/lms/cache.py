"""Simple in-memory cache utilities for Phase 5."""

from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any, Dict, Optional


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0


class TTLCache:
    """Basic TTL cache with hit/miss tracking."""

    def __init__(self, default_ttl_seconds: int = 1800):
        self.default_ttl_seconds = default_ttl_seconds
        self._store: Dict[str, tuple] = {}
        self.stats = CacheStats()

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        expires_at = time() + ttl
        self._store[key] = (value, expires_at)

    def get(self, key: str) -> Optional[Any]:
        record = self._store.get(key)
        if not record:
            self.stats.misses += 1
            return None

        value, expires_at = record
        if time() >= expires_at:
            self._store.pop(key, None)
            self.stats.misses += 1
            return None

        self.stats.hits += 1
        return value

    def clear(self) -> None:
        self._store.clear()
        self.stats = CacheStats()
