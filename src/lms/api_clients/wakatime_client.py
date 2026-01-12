"""WakaTime API client for tracking coding statistics."""

import base64
import os
from datetime import date
from typing import Optional
import requests
from requests.exceptions import RequestException, Timeout


class WakaTimeError(Exception):
    """Base exception for WakaTime API errors."""

    pass


class WakaTimeAuthError(WakaTimeError):
    """Authentication error (invalid API key)."""

    pass


class WakaTimeRateLimitError(WakaTimeError):
    """Rate limit exceeded."""

    pass


class WakaTimeClient:
    """Client for interacting with the WakaTime API.

    This client handles authentication and retrieves coding statistics
    from WakaTime for specific dates.
    """

    BASE_URL = "https://wakatime.com/api/v1"
    TIMEOUT = 10  # seconds

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the WakaTime client.

        Args:
            api_key: WakaTime API key. If None, reads from WAKATIME_API_KEY env var.

        Raises:
            WakaTimeAuthError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("WAKATIME_API_KEY")
        if not self.api_key:
            raise WakaTimeAuthError(
                "WakaTime API key not provided. Set WAKATIME_API_KEY environment variable."
            )

        # WakaTime uses HTTP Basic Auth with API key as username (no password)
        # Encode "api_key:" in base64 and prepend "Basic "
        credentials = base64.b64encode(f"{self.api_key}:".encode()).decode()

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Basic {credentials}"})

    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a request to the WakaTime API.

        Args:
            endpoint: API endpoint path (e.g., "/users/current/summaries").
            params: Optional query parameters.

        Returns:
            JSON response as dictionary.

        Raises:
            WakaTimeAuthError: If authentication fails (401).
            WakaTimeRateLimitError: If rate limit is exceeded (429).
            WakaTimeError: For other API errors.
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)

            if response.status_code == 401:
                raise WakaTimeAuthError("Invalid WakaTime API key (401 Unauthorized)")
            elif response.status_code == 429:
                raise WakaTimeRateLimitError(
                    "WakaTime API rate limit exceeded. Please try again later."
                )
            elif response.status_code != 200:
                raise WakaTimeError(
                    f"WakaTime API error: {response.status_code} - {response.text}"
                )

            return response.json()

        except Timeout:
            raise WakaTimeError(
                f"Request to WakaTime API timed out after {self.TIMEOUT} seconds"
            )
        except RequestException as e:
            raise WakaTimeError(f"Network error while contacting WakaTime API: {e}")

    def get_today_stats(self) -> dict:
        """Get coding statistics for today.

        Returns:
            Dictionary with keys:
                - total_seconds: Total time coded today (int)
                - languages: List of languages used with time spent
                - categories: List of categories with time spent
                - formatted_time: Human-readable time string

        Raises:
            WakaTimeError: If API request fails.
        """
        today = date.today().isoformat()
        return self.get_date_stats(today)

    def get_date_stats(self, target_date: str) -> dict:
        """Get coding statistics for a specific date.

        Args:
            target_date: Date in YYYY-MM-DD format.

        Returns:
            Dictionary with keys:
                - total_seconds: Total time coded (int)
                - languages: List of languages used with time spent
                - categories: List of categories with time spent
                - formatted_time: Human-readable time string
                - date: The date of the stats

        Raises:
            WakaTimeError: If API request fails.
        """
        params = {"start": target_date, "end": target_date}

        response = self._make_request("/users/current/summaries", params=params)

        # Extract data from response
        if not response.get("data"):
            return {
                "date": target_date,
                "total_seconds": 0,
                "languages": [],
                "categories": [],
                "formatted_time": "0h 00min",
            }

        day_data = response["data"][0]
        grand_total = day_data.get("grand_total", {})

        return {
            "date": target_date,
            "total_seconds": grand_total.get("total_seconds", 0),
            "languages": day_data.get("languages", []),
            "categories": day_data.get("categories", []),
            "formatted_time": grand_total.get("text", "0h 00min"),
        }

    def get_week_stats(self, start_date: str, end_date: str) -> list[dict]:
        """Get coding statistics for a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            List of daily stat dictionaries.

        Raises:
            WakaTimeError: If API request fails.
        """
        params = {"start": start_date, "end": end_date}

        response = self._make_request("/users/current/summaries", params=params)

        if not response.get("data"):
            return []

        stats = []
        for day_data in response["data"]:
            grand_total = day_data.get("grand_total", {})
            stats.append(
                {
                    "date": day_data.get("range", {}).get("date", ""),
                    "total_seconds": grand_total.get("total_seconds", 0),
                    "languages": day_data.get("languages", []),
                    "categories": day_data.get("categories", []),
                    "formatted_time": grand_total.get("text", "0h 00min"),
                }
            )

        return stats
