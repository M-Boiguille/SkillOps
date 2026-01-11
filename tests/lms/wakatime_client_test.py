"""
Test suite for WakaTimeClient class.

Based on:
- URD (User Requirements Document) - US-001: Tracking de Formation WakaTime
- Sprint Planning Sprint 1 - Task T001-1: Setup WakaTime API client
- Testing pattern from tests/lms/metrics_manager_test.py

WakaTimeClient responsibilities:
1. Authenticate with WakaTime API using API key
2. Fetch today's coding statistics
3. Fetch coding statistics for specific dates
4. Handle API errors (rate limits, network issues, authentication)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
import requests
from lms.api_clients.wakatime_client import (
    WakaTimeClient,
    WakaTimeAPIError,
    WakaTimeAuthError,
    WakaTimeRateLimitError
)


class TestWakaTimeClientInit:
    """Test WakaTimeClient initialization and configuration."""

    def test_init_with_valid_api_key(self):
        """
        Given: A valid API key
        When: WakaTimeClient is initialized
        Then: It should create instance with correct api_key and session headers
        """
        api_key = "waka_test_key_123"
        client = WakaTimeClient(api_key)
        
        assert client.api_key == api_key
        assert client.session.headers["Authorization"] == f"Bearer {api_key}"

    def test_init_with_empty_api_key_raises_error(self):
        """
        Given: An empty API key
        When: WakaTimeClient is initialized
        Then: It should raise ValueError
        """
        with pytest.raises(ValueError, match="API key is required"):
            WakaTimeClient("")

    def test_init_with_none_api_key_raises_error(self):
        """
        Given: None as API key
        When: WakaTimeClient is initialized
        Then: It should raise ValueError
        """
        with pytest.raises(ValueError, match="API key is required"):
            WakaTimeClient(None)


class TestGetTodayStats:
    """Test fetching today's coding statistics."""

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_today_stats_success(self, mock_get):
        """
        Given: A WakaTime client with valid API key
        When: get_today_stats is called and API returns success
        Then: It should return today's statistics
        """
        # Arrange
        api_key = "waka_test_key"
        client = WakaTimeClient(api_key)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{
                "grand_total": {
                    "text": "3 hrs 42 mins",
                    "total_seconds": 13320
                },
                "languages": [
                    {"name": "Python", "total_seconds": 10000},
                    {"name": "JavaScript", "total_seconds": 3320}
                ],
                "projects": [
                    {"name": "SkillOps", "total_seconds": 13320}
                ]
            }]
        }
        mock_get.return_value = mock_response
        
        # Act
        result = client.get_today_stats()
        
        # Assert
        assert result["grand_total"]["text"] == "3 hrs 42 mins"
        assert result["grand_total"]["total_seconds"] == 13320
        assert len(result["languages"]) == 2
        assert len(result["projects"]) == 1
        
        # Verify API was called with today's date
        today = date.today().isoformat()
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["start"] == today
        assert call_args[1]["params"]["end"] == today

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_today_stats_no_data_returns_empty_structure(self, mock_get):
        """
        Given: A WakaTime client
        When: get_today_stats is called and API returns no data
        Then: It should return empty statistics structure
        """
        # Arrange
        client = WakaTimeClient("test_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        # Act
        result = client.get_today_stats()
        
        # Assert
        assert result["grand_total"]["text"] == "0 secs"
        assert result["grand_total"]["total_seconds"] == 0
        assert result["languages"] == []
        assert result["projects"] == []


class TestGetDateStats:
    """Test fetching coding statistics for specific dates."""

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_with_valid_date(self, mock_get):
        """
        Given: A WakaTime client and valid date
        When: get_date_stats is called
        Then: It should return statistics for that date
        """
        # Arrange
        client = WakaTimeClient("test_key")
        test_date = "2026-01-10"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{
                "grand_total": {
                    "text": "2 hrs 15 mins",
                    "total_seconds": 8100
                },
                "languages": [{"name": "Python", "total_seconds": 8100}],
                "projects": []
            }]
        }
        mock_get.return_value = mock_response
        
        # Act
        result = client.get_date_stats(test_date)
        
        # Assert
        assert result["grand_total"]["total_seconds"] == 8100
        
        # Verify correct endpoint and params
        call_args = mock_get.call_args
        assert "users/current/summaries" in call_args[0][0]
        assert call_args[1]["params"]["start"] == test_date
        assert call_args[1]["params"]["end"] == test_date

    def test_get_date_stats_with_invalid_date_format(self):
        """
        Given: A WakaTime client
        When: get_date_stats is called with invalid date format
        Then: It should raise ValueError
        """
        client = WakaTimeClient("test_key")
        
        with pytest.raises(ValueError, match="Invalid date format"):
            client.get_date_stats("01/10/2026")

    def test_get_date_stats_with_invalid_date_string(self):
        """
        Given: A WakaTime client
        When: get_date_stats is called with invalid date string
        Then: It should raise ValueError
        """
        client = WakaTimeClient("test_key")
        
        with pytest.raises(ValueError, match="Invalid date format"):
            client.get_date_stats("not-a-date")

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_empty_data_returns_empty_structure(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called and API returns empty data
        Then: It should return empty statistics structure
        """
        # Arrange
        client = WakaTimeClient("test_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        # Act
        result = client.get_date_stats("2026-01-01")
        
        # Assert
        assert result["grand_total"]["total_seconds"] == 0
        assert result["languages"] == []
        assert result["projects"] == []


class TestErrorHandling:
    """Test error handling for various failure scenarios."""

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_401_raises_auth_error(self, mock_get):
        """
        Given: A WakaTime client with invalid API key
        When: get_date_stats is called and API returns 401
        Then: It should raise WakaTimeAuthError
        """
        client = WakaTimeClient("invalid_key")
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        with pytest.raises(WakaTimeAuthError, match="Authentication failed"):
            client.get_date_stats("2026-01-10")

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_429_raises_rate_limit_error(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called and API returns 429
        Then: It should raise WakaTimeRateLimitError
        """
        client = WakaTimeClient("test_key")
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_get.return_value = mock_response
        
        with pytest.raises(WakaTimeRateLimitError, match="Rate limit exceeded"):
            client.get_date_stats("2026-01-10")

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_500_raises_api_error(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called and API returns 500
        Then: It should raise WakaTimeAPIError
        """
        client = WakaTimeClient("test_key")
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        with pytest.raises(WakaTimeAPIError, match="API request failed with status 500"):
            client.get_date_stats("2026-01-10")

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_timeout_raises_api_error(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called and request times out
        Then: It should raise WakaTimeAPIError with timeout message
        """
        client = WakaTimeClient("test_key")
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(WakaTimeAPIError, match="Request timed out"):
            client.get_date_stats("2026-01-10")

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_connection_error_raises_api_error(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called and connection fails
        Then: It should raise WakaTimeAPIError with connection error message
        """
        client = WakaTimeClient("test_key")
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(WakaTimeAPIError, match="Connection error"):
            client.get_date_stats("2026-01-10")

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_request_exception_raises_api_error(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called and generic request exception occurs
        Then: It should raise WakaTimeAPIError with network error message
        """
        client = WakaTimeClient("test_key")
        mock_get.side_effect = requests.exceptions.RequestException("Network issue")
        
        with pytest.raises(WakaTimeAPIError, match="Network error occurred"):
            client.get_date_stats("2026-01-10")


class TestAuthenticationHeaders:
    """Test authentication header configuration."""

    def test_session_has_authorization_header(self):
        """
        Given: A WakaTime client
        When: Client is initialized with API key
        Then: Session should have Authorization header with Bearer token
        """
        api_key = "test_api_key_xyz"
        client = WakaTimeClient(api_key)
        
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == f"Bearer {api_key}"

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_requests_include_authorization_header(self, mock_get):
        """
        Given: A WakaTime client
        When: API request is made
        Then: Request should include Authorization header
        """
        api_key = "test_key_123"
        client = WakaTimeClient(api_key)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        client.get_date_stats("2026-01-10")
        
        # Verify the session was configured with auth header
        assert client.session.headers["Authorization"] == f"Bearer {api_key}"


class TestAPIEndpoints:
    """Test correct API endpoint construction."""

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_uses_correct_endpoint(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called
        Then: It should call the correct WakaTime API endpoint
        """
        client = WakaTimeClient("test_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        client.get_date_stats("2026-01-10")
        
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://wakatime.com/api/v1/users/current/summaries"

    @patch('lms.api_clients.wakatime_client.requests.Session.get')
    def test_get_date_stats_includes_timeout(self, mock_get):
        """
        Given: A WakaTime client
        When: get_date_stats is called
        Then: Request should include timeout parameter
        """
        client = WakaTimeClient("test_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response
        
        client.get_date_stats("2026-01-10")
        
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 10
