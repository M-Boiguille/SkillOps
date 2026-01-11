"""WakaTime API client for fetching coding time statistics.

This module provides a client for interacting with the WakaTime API to retrieve
coding statistics. It includes retry logic with exponential backoff for handling
rate limits and network errors.

Based on:
- Sprint Planning Sprint 1 - Task T001-1: Setup WakaTime API client
- WakaTime API Documentation: https://wakatime.com/developers
"""

from datetime import date, timedelta
from typing import Any
import time
import requests


class WakaTimeError(Exception):
    """Base exception for WakaTime API errors."""
    pass


class WakaTimeAuthError(WakaTimeError):
    """Exception raised for authentication errors (401)."""
    pass


class WakaTimeRateLimitError(WakaTimeError):
    """Exception raised when API rate limit is exceeded (429)."""
    pass


class WakaTimeNetworkError(WakaTimeError):
    """Exception raised for network-related errors."""
    pass


class WakaTimeClient:
    """Client for interacting with WakaTime API.
    
    Responsibilities:
    - Authenticate with WakaTime API using API key
    - Fetch daily coding statistics
    - Handle API errors (401, 429, network errors)
    - Implement retry logic with exponential backoff
    - Parse JSON responses
    
    Example:
        client = WakaTimeClient(api_key="waka_xxx")
        stats = client.get_today_stats()
        print(f"Coded today: {stats['grand_total']['text']}")
    """

    BASE_URL = "https://wakatime.com/api/v1"
    
    def __init__(self, api_key: str, max_retries: int = 3):
        """Initialize WakaTime client.
        
        Args:
            api_key: WakaTime API key (format: waka_xxx)
            max_retries: Maximum number of retry attempts for failed requests
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })
    
    def _make_request(
        self, 
        endpoint: str, 
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make HTTP request to WakaTime API with retry logic.
        
        Args:
            endpoint: API endpoint (e.g., "/users/current/summaries")
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            WakaTimeAuthError: If authentication fails (401)
            WakaTimeRateLimitError: If rate limit exceeded (429)
            WakaTimeNetworkError: If network error occurs
        """
        url = f"{self.BASE_URL}{endpoint}"
        retry_delay = 1.0  # Start with 1 second
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                # Handle different status codes
                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code == 401:
                    raise WakaTimeAuthError("Invalid API key or unauthorized access")
                
                elif response.status_code == 429:
                    # Rate limit - retry with backoff
                    if attempt < self.max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    raise WakaTimeRateLimitError("API rate limit exceeded")
                
                else:
                    # Other errors
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout as e:
                if attempt < self.max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise WakaTimeNetworkError(f"Request timeout: {e}") from e
            
            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise WakaTimeNetworkError(f"Connection error: {e}") from e
            
            except requests.exceptions.RequestException as e:
                raise WakaTimeNetworkError(f"Network error: {e}") from e
        
        # Should not reach here, but just in case
        raise WakaTimeError("Max retries exceeded")
    
    def get_summaries(self, start_date: str, end_date: str) -> dict[str, Any]:
        """Get coding summaries for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing summaries data with structure:
            {
                "data": [
                    {
                        "grand_total": {"text": "3 hrs 42 mins", "total_seconds": 13320},
                        "languages": [...],
                        "range": {"date": "2024-01-10", ...}
                    }
                ]
            }
        """
        params = {
            "start": start_date,
            "end": end_date
        }
        return self._make_request("/users/current/summaries", params)
    
    def get_today_stats(self) -> dict[str, Any]:
        """Get coding statistics for today.
        
        Returns:
            Dictionary with today's coding stats, or empty stats if no data
        """
        today = date.today().strftime("%Y-%m-%d")
        response = self.get_summaries(today, today)
        
        # Extract first (and only) day's data
        if response.get("data") and len(response["data"]) > 0:
            return response["data"][0]
        
        # Return empty stats if no data for today
        return {
            "grand_total": {"text": "0 secs", "total_seconds": 0},
            "languages": [],
            "range": {"date": today}
        }
    
    def get_date_stats(self, date_str: str) -> dict[str, Any]:
        """Get coding statistics for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with that date's coding stats, or empty stats if no data
        """
        response = self.get_summaries(date_str, date_str)
        
        # Extract first (and only) day's data
        if response.get("data") and len(response["data"]) > 0:
            return response["data"][0]
        
        # Return empty stats if no data for that date
        return {
            "grand_total": {"text": "0 secs", "total_seconds": 0},
            "languages": [],
            "range": {"date": date_str}
        }
