"""Tests for WakaTime API client."""

import base64
import pytest
import os
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, RequestException
from src.lms.api_clients.wakatime_client import (
    WakaTimeClient,
    WakaTimeError,
    WakaTimeAuthError,
    WakaTimeRateLimitError,
)


class TestWakaTimeClientInit:
    """Tests for WakaTimeClient initialization."""

    def test_init_with_api_key(self):
        """
        Given: API key provided directly
        When: Creating WakaTimeClient
        Then: Client is initialized with the key using Basic Auth
        """
        client = WakaTimeClient(api_key="test_key_123")

        assert client.api_key == "test_key_123"
        assert "Authorization" in client.session.headers
        # WakaTime uses HTTP Basic Auth with api_key:password format (password is empty)
        expected_credentials = base64.b64encode(b"test_key_123:").decode()
        assert (
            client.session.headers["Authorization"] == f"Basic {expected_credentials}"
        )

    @patch.dict(os.environ, {"WAKATIME_API_KEY": "env_key_456"})
    def test_init_from_environment(self):
        """
        Given: API key in environment variable
        When: Creating WakaTimeClient without explicit key
        Then: Client reads key from environment
        """
        client = WakaTimeClient()

        assert client.api_key == "env_key_456"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_no_api_key_raises_error(self):
        """
        Given: No API key provided or in environment
        When: Creating WakaTimeClient
        Then: Raises WakaTimeAuthError
        """
        with pytest.raises(WakaTimeAuthError) as exc_info:
            WakaTimeClient()

        assert "API key not provided" in str(exc_info.value)


class TestMakeRequest:
    """Tests for _make_request method."""

    @patch("src.lms.api_clients.wakatime_client.requests.Session.get")
    def test_make_request_success(self, mock_get):
        """
        Given: Successful API response
        When: Making request
        Then: Returns parsed JSON
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        client = WakaTimeClient(api_key="test_key")
        result = client._make_request("/test")

        assert result == {"data": "test"}
        mock_get.assert_called_once()

    @patch("src.lms.api_clients.wakatime_client.requests.Session.get")
    def test_make_request_401_raises_auth_error(self, mock_get):
        """
        Given: API returns 401 Unauthorized
        When: Making request
        Then: Raises WakaTimeAuthError
        """
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        client = WakaTimeClient(api_key="invalid_key")

        with pytest.raises(WakaTimeAuthError) as exc_info:
            client._make_request("/test")

        assert "Invalid WakaTime API key" in str(exc_info.value)

    @patch("src.lms.api_clients.wakatime_client.requests.Session.get")
    def test_make_request_429_raises_rate_limit_error(self, mock_get):
        """
        Given: API returns 429 Too Many Requests
        When: Making request
        Then: Raises WakaTimeRateLimitError
        """
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        client = WakaTimeClient(api_key="test_key")

        with pytest.raises(WakaTimeRateLimitError) as exc_info:
            client._make_request("/test")

        assert "rate limit exceeded" in str(exc_info.value)

    @patch("src.lms.api_clients.wakatime_client.requests.Session.get")
    def test_make_request_other_error_code(self, mock_get):
        """
        Given: API returns non-200/401/429 status code
        When: Making request
        Then: Raises generic WakaTimeError
        """
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response

        client = WakaTimeClient(api_key="test_key")

        with pytest.raises(WakaTimeError) as exc_info:
            client._make_request("/test")

        assert "500" in str(exc_info.value)

    @patch("src.lms.api_clients.wakatime_client.requests.Session.get")
    def test_make_request_timeout(self, mock_get):
        """
        Given: Request times out
        When: Making request
        Then: Raises WakaTimeError with timeout message
        """
        mock_get.side_effect = Timeout()

        client = WakaTimeClient(api_key="test_key")

        with pytest.raises(WakaTimeError) as exc_info:
            client._make_request("/test")

        assert "timed out" in str(exc_info.value)

    @patch("src.lms.api_clients.wakatime_client.requests.Session.get")
    def test_make_request_network_error(self, mock_get):
        """
        Given: Network error occurs
        When: Making request
        Then: Raises WakaTimeError with network error message
        """
        mock_get.side_effect = RequestException("Connection failed")

        client = WakaTimeClient(api_key="test_key")

        with pytest.raises(WakaTimeError) as exc_info:
            client._make_request("/test")

        assert "Network error" in str(exc_info.value)


class TestGetTodayStats:
    """Tests for get_today_stats method."""

    @patch("src.lms.api_clients.wakatime_client.date")
    @patch.object(WakaTimeClient, "get_date_stats")
    def test_get_today_stats_calls_get_date_stats(self, mock_get_date_stats, mock_date):
        """
        Given: WakaTimeClient instance
        When: Calling get_today_stats
        Then: Calls get_date_stats with today's date
        """
        mock_date.today.return_value.isoformat.return_value = "2026-01-11"
        mock_get_date_stats.return_value = {"total_seconds": 3600}

        client = WakaTimeClient(api_key="test_key")
        result = client.get_today_stats()

        mock_get_date_stats.assert_called_once_with("2026-01-11")
        assert result == {"total_seconds": 3600}


class TestGetDateStats:
    """Tests for get_date_stats method."""

    @patch.object(WakaTimeClient, "_make_request")
    def test_get_date_stats_with_data(self, mock_make_request):
        """
        Given: API returns data for requested date
        When: Getting date stats
        Then: Returns properly formatted stats
        """
        mock_make_request.return_value = {
            "data": [
                {
                    "grand_total": {"total_seconds": 7200, "text": "2h 00min"},
                    "languages": [{"name": "Python", "total_seconds": 5400}],
                    "categories": [{"name": "Coding", "total_seconds": 7200}],
                }
            ]
        }

        client = WakaTimeClient(api_key="test_key")
        result = client.get_date_stats("2026-01-10")

        assert result["date"] == "2026-01-10"
        assert result["total_seconds"] == 7200
        assert result["formatted_time"] == "2h 00min"
        assert len(result["languages"]) == 1
        assert result["languages"][0]["name"] == "Python"

    @patch.object(WakaTimeClient, "_make_request")
    def test_get_date_stats_no_data(self, mock_make_request):
        """
        Given: API returns no data (no activity on date)
        When: Getting date stats
        Then: Returns zero stats
        """
        mock_make_request.return_value = {"data": []}

        client = WakaTimeClient(api_key="test_key")
        result = client.get_date_stats("2026-01-10")

        assert result["date"] == "2026-01-10"
        assert result["total_seconds"] == 0
        assert result["formatted_time"] == "0h 00min"
        assert result["languages"] == []


class TestGetWeekStats:
    """Tests for get_week_stats method."""

    @patch.object(WakaTimeClient, "_make_request")
    def test_get_week_stats_with_data(self, mock_make_request):
        """
        Given: API returns data for date range
        When: Getting week stats
        Then: Returns list of daily stats
        """
        mock_make_request.return_value = {
            "data": [
                {
                    "range": {"date": "2026-01-06"},
                    "grand_total": {"total_seconds": 5400, "text": "1h 30min"},
                    "languages": [],
                    "categories": [],
                },
                {
                    "range": {"date": "2026-01-07"},
                    "grand_total": {"total_seconds": 7200, "text": "2h 00min"},
                    "languages": [],
                    "categories": [],
                },
            ]
        }

        client = WakaTimeClient(api_key="test_key")
        result = client.get_week_stats("2026-01-06", "2026-01-07")

        assert len(result) == 2
        assert result[0]["date"] == "2026-01-06"
        assert result[0]["total_seconds"] == 5400
        assert result[1]["date"] == "2026-01-07"
        assert result[1]["total_seconds"] == 7200

    @patch.object(WakaTimeClient, "_make_request")
    def test_get_week_stats_no_data(self, mock_make_request):
        """
        Given: API returns no data for date range
        When: Getting week stats
        Then: Returns empty list
        """
        mock_make_request.return_value = {"data": []}

        client = WakaTimeClient(api_key="test_key")
        result = client.get_week_stats("2026-01-06", "2026-01-07")

        assert result == []


class TestIntegration:
    """Integration tests for WakaTimeClient."""

    @patch("src.lms.api_clients.wakatime_client.requests.Session.get")
    def test_full_workflow(self, mock_get):
        """
        Given: Complete API response
        When: Using client methods
        Then: All data is correctly extracted
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "grand_total": {"total_seconds": 10800, "text": "3h 00min"},
                    "languages": [
                        {"name": "Python", "total_seconds": 8000},
                        {"name": "JavaScript", "total_seconds": 2800},
                    ],
                    "categories": [{"name": "Coding", "total_seconds": 10800}],
                }
            ]
        }
        mock_get.return_value = mock_response

        client = WakaTimeClient(api_key="test_key")
        stats = client.get_date_stats("2026-01-11")

        assert stats["total_seconds"] == 10800
        assert len(stats["languages"]) == 2
        assert stats["languages"][0]["name"] == "Python"
