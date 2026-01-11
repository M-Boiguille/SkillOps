"""
WakaTime API Client for tracking coding time statistics.

Based on:
- URD (User Requirements Document) - US-001: Tracking de Formation WakaTime
- Sprint Planning Sprint 1 - Task T001-1: Setup WakaTime API client
- WakaTime API Documentation: https://wakatime.com/developers

Responsibilities:
1. Authenticate with WakaTime API using API key
2. Fetch today's coding statistics
3. Fetch coding statistics for specific dates
4. Handle API errors (rate limits, network issues, authentication)
"""

import requests
from typing import Dict, Optional, Any
from datetime import datetime, date


class WakaTimeClient:
    """Client for interacting with WakaTime API.
    
    Handles authentication and retrieval of coding time statistics
    from WakaTime's summaries endpoint.
    """

    BASE_URL = "https://wakatime.com/api/v1"
    
    def __init__(self, api_key: str):
        """Initialize WakaTime client with API key.
        
        Args:
            api_key: WakaTime API key for authentication
            
        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })

    def get_today_stats(self) -> Dict[str, Any]:
        """Fetch coding statistics for today.
        
        Returns:
            Dictionary containing today's coding statistics including:
            - grand_total: Total time coded
            - languages: List of languages used
            - projects: List of projects worked on
            
        Raises:
            WakaTimeAPIError: If API request fails
            WakaTimeAuthError: If authentication fails (401)
            WakaTimeRateLimitError: If rate limit is exceeded (429)
        """
        today = date.today().isoformat()
        return self.get_date_stats(today)

    def get_date_stats(self, date_str: str) -> Dict[str, Any]:
        """Fetch coding statistics for a specific date.
        
        Args:
            date_str: Date in ISO format (YYYY-MM-DD)
            
        Returns:
            Dictionary containing coding statistics for the specified date
            
        Raises:
            ValueError: If date format is invalid
            WakaTimeAPIError: If API request fails
            WakaTimeAuthError: If authentication fails (401)
            WakaTimeRateLimitError: If rate limit is exceeded (429)
        """
        # Validate date format
        try:
            datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
        
        endpoint = f"{self.BASE_URL}/users/current/summaries"
        params = {
            "start": date_str,
            "end": date_str
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                raise WakaTimeAuthError("Authentication failed. Check your API key.")
            elif response.status_code == 429:
                raise WakaTimeRateLimitError("Rate limit exceeded. Please try again later.")
            elif response.status_code != 200:
                raise WakaTimeAPIError(
                    f"API request failed with status {response.status_code}: {response.text}"
                )
            
            data = response.json()
            
            # Return the first summary (should be only one for single-day range)
            if data.get("data") and len(data["data"]) > 0:
                summary: Dict[str, Any] = data["data"][0]
                return summary
            else:
                # Return empty stats structure if no data available
                return {
                    "grand_total": {"text": "0 secs", "total_seconds": 0},
                    "languages": [],
                    "projects": []
                }
                
        except requests.exceptions.Timeout:
            raise WakaTimeAPIError("Request timed out. Please check your network connection.")
        except requests.exceptions.ConnectionError:
            raise WakaTimeAPIError("Connection error. Please check your network connection.")
        except requests.exceptions.RequestException as e:
            raise WakaTimeAPIError(f"Network error occurred: {str(e)}")


class WakaTimeAPIError(Exception):
    """Base exception for WakaTime API errors."""
    pass


class WakaTimeAuthError(WakaTimeAPIError):
    """Exception raised when authentication fails (401)."""
    pass


class WakaTimeRateLimitError(WakaTimeAPIError):
    """Exception raised when rate limit is exceeded (429)."""
    pass
