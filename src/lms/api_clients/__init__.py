"""API clients package."""

from lms.api_clients.wakatime_client import (
    WakaTimeClient,
    WakaTimeError,
    WakaTimeAuthError,
    WakaTimeRateLimitError,
)

__all__ = [
    "WakaTimeClient",
    "WakaTimeError",
    "WakaTimeAuthError",
    "WakaTimeRateLimitError",
]

