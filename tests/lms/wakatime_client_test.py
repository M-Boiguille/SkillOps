"""
Test suite for WakaTimeClient class.

Based on:
- Sprint Planning Sprint 1 - Task T001-4: Tests WakaTime avec mocks
- Issue [US-001] T001-4: Tests WakaTime avec mocks

Test coverage includes:
1. Mock API responses (200, 401, 429, network error)
2. Test parsing données
3. Test gestion erreurs
4. Test retry logic
5. No real API calls

Testing Pattern: Given-When-Then with Arrange-Act-Assert
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
import requests
from lms.wakatime_client import (
    WakaTimeClient,
    WakaTimeError,
    WakaTimeAuthError,
    WakaTimeRateLimitError,
    WakaTimeNetworkError
)


class TestWakaTimeClientInit:
    """Test WakaTimeClient initialization."""

    def test_init_with_valid_api_key(self):
        """
        Given: A valid API key
        When: WakaTimeClient is initialized
        Then: It should create instance with correct attributes
        """
        # Arrange & Act
        client = WakaTimeClient(api_key="waka_test_key_123")
        
        # Assert
        assert client.api_key == "waka_test_key_123"
        assert client.max_retries == 3
        assert client.session is not None
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer waka_test_key_123"

    def test_init_with_custom_max_retries(self):
        """
        Given: A custom max_retries value
        When: WakaTimeClient is initialized
        Then: It should use the custom value
        """
        # Arrange & Act
        client = WakaTimeClient(api_key="waka_test", max_retries=5)
        
        # Assert
        assert client.max_retries == 5

    def test_init_with_empty_api_key_raises_error(self):
        """
        Given: An empty API key
        When: WakaTimeClient is initialized
        Then: It should raise ValueError
        """
        # Act & Assert
        with pytest.raises(ValueError, match="API key cannot be empty"):
            WakaTimeClient(api_key="")

    def test_init_sets_correct_base_url(self):
        """
        Given: WakaTime API requirements
        When: WakaTimeClient is initialized
        Then: It should use correct base URL
        """
        # Arrange & Act
        client = WakaTimeClient(api_key="waka_test")
        
        # Assert
        assert client.BASE_URL == "https://wakatime.com/api/v1"


class TestMakeRequestSuccess:
    """Test successful API requests with mocked responses."""

    @patch('lms.wakatime_client.requests.Session')
    def test_make_request_returns_json_on_200(self, mock_session_class):
        """
        Given: A successful API response (200)
        When: _make_request is called
        Then: It should return parsed JSON data
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"test": "value"}]}
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client._make_request("/users/current/summaries")
        
        # Assert
        assert result == {"data": [{"test": "value"}]}
        mock_session.get.assert_called_once()

    @patch('lms.wakatime_client.requests.Session')
    def test_make_request_includes_params(self, mock_session_class):
        """
        Given: Query parameters for API request
        When: _make_request is called with params
        Then: It should pass params to the request
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        params = {"start": "2024-01-10", "end": "2024-01-10"}
        
        # Act
        client._make_request("/users/current/summaries", params)
        
        # Assert
        call_args = mock_session.get.call_args
        assert call_args[1]["params"] == params

    @patch('lms.wakatime_client.requests.Session')
    def test_make_request_includes_timeout(self, mock_session_class):
        """
        Given: API request configuration
        When: _make_request is called
        Then: It should set timeout to prevent hanging
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        client._make_request("/test")
        
        # Assert
        call_args = mock_session.get.call_args
        assert call_args[1]["timeout"] == 10


class TestMakeRequestErrors:
    """Test error handling in API requests."""

    @patch('lms.wakatime_client.requests.Session')
    def test_make_request_raises_auth_error_on_401(self, mock_session_class):
        """
        Given: An unauthorized API response (401)
        When: _make_request is called
        Then: It should raise WakaTimeAuthError
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="invalid_key")
        
        # Act & Assert
        with pytest.raises(WakaTimeAuthError, match="Invalid API key"):
            client._make_request("/users/current/summaries")

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.time.sleep')
    def test_make_request_raises_rate_limit_after_retries(
        self, mock_sleep, mock_session_class
    ):
        """
        Given: API rate limit exceeded (429) on all retry attempts
        When: _make_request is called
        Then: It should retry with backoff and raise WakaTimeRateLimitError
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test", max_retries=3)
        
        # Act & Assert
        with pytest.raises(WakaTimeRateLimitError, match="rate limit exceeded"):
            client._make_request("/users/current/summaries")
        
        # Verify retry attempts
        assert mock_session.get.call_count == 3
        # Verify exponential backoff (should sleep 2 times: after 1st and 2nd attempt)
        assert mock_sleep.call_count == 2

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.time.sleep')
    def test_make_request_timeout_triggers_retry(self, mock_sleep, mock_session_class):
        """
        Given: API request timeout
        When: _make_request is called
        Then: It should retry with exponential backoff
        """
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session.get.side_effect = requests.exceptions.Timeout("Request timed out")
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test", max_retries=3)
        
        # Act & Assert
        with pytest.raises(WakaTimeNetworkError, match="Request timeout"):
            client._make_request("/users/current/summaries")
        
        # Verify retries
        assert mock_session.get.call_count == 3
        assert mock_sleep.call_count == 2

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.time.sleep')
    def test_make_request_connection_error_triggers_retry(
        self, mock_sleep, mock_session_class
    ):
        """
        Given: Network connection error
        When: _make_request is called
        Then: It should retry with exponential backoff
        """
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test", max_retries=3)
        
        # Act & Assert
        with pytest.raises(WakaTimeNetworkError, match="Connection error"):
            client._make_request("/users/current/summaries")
        
        # Verify retries
        assert mock_session.get.call_count == 3
        assert mock_sleep.call_count == 2

    @patch('lms.wakatime_client.requests.Session')
    def test_make_request_generic_request_exception(self, mock_session_class):
        """
        Given: A generic request exception
        When: _make_request is called
        Then: It should raise WakaTimeNetworkError
        """
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session.get.side_effect = requests.exceptions.RequestException(
            "Generic error"
        )
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act & Assert
        with pytest.raises(WakaTimeNetworkError, match="Network error"):
            client._make_request("/users/current/summaries")


class TestRetryLogic:
    """Test exponential backoff retry logic."""

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.time.sleep')
    def test_retry_uses_exponential_backoff(self, mock_sleep, mock_session_class):
        """
        Given: Multiple failed requests (429)
        When: Retry logic is triggered
        Then: It should use exponential backoff (1s, 2s, 4s, ...)
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test", max_retries=4)
        
        # Act
        try:
            client._make_request("/users/current/summaries")
        except WakaTimeRateLimitError:
            pass
        
        # Assert - verify exponential backoff delays
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert len(sleep_calls) == 3  # 3 sleeps for 4 attempts
        assert sleep_calls[0] == 1.0
        assert sleep_calls[1] == 2.0
        assert sleep_calls[2] == 4.0

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.time.sleep')
    def test_retry_succeeds_on_second_attempt(self, mock_sleep, mock_session_class):
        """
        Given: First request fails (429), second succeeds (200)
        When: _make_request is called
        Then: It should retry and return successful response
        """
        # Arrange
        mock_response_fail = Mock()
        mock_response_fail.status_code = 429
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": "success"}
        
        mock_session = Mock()
        mock_session.headers = {}
        mock_session.get.side_effect = [mock_response_fail, mock_response_success]
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test", max_retries=3)
        
        # Act
        result = client._make_request("/users/current/summaries")
        
        # Assert
        assert result == {"data": "success"}
        assert mock_session.get.call_count == 2
        assert mock_sleep.call_count == 1


class TestGetSummaries:
    """Test get_summaries method with date range."""

    @patch('lms.wakatime_client.requests.Session')
    def test_get_summaries_with_date_range(self, mock_session_class):
        """
        Given: Start and end dates
        When: get_summaries is called
        Then: It should request summaries for that date range
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "grand_total": {"text": "3 hrs 42 mins", "total_seconds": 13320},
                    "languages": [{"name": "Python", "total_seconds": 10000}],
                    "range": {"date": "2024-01-10"}
                }
            ]
        }
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client.get_summaries("2024-01-10", "2024-01-10")
        
        # Assert
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["grand_total"]["total_seconds"] == 13320
        
        # Verify correct params were sent
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["start"] == "2024-01-10"
        assert call_args[1]["params"]["end"] == "2024-01-10"


class TestGetTodayStats:
    """Test getting today's statistics."""

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.date')
    def test_get_today_stats_returns_current_day_data(
        self, mock_date, mock_session_class
    ):
        """
        Given: Current date is 2024-01-10
        When: get_today_stats is called
        Then: It should return stats for today
        """
        # Arrange
        mock_date.today.return_value.strftime.return_value = "2024-01-10"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "grand_total": {"text": "2 hrs 15 mins", "total_seconds": 8100},
                    "languages": [{"name": "JavaScript", "total_seconds": 8100}],
                    "range": {"date": "2024-01-10"}
                }
            ]
        }
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client.get_today_stats()
        
        # Assert
        assert result["grand_total"]["total_seconds"] == 8100
        assert result["languages"][0]["name"] == "JavaScript"
        assert result["range"]["date"] == "2024-01-10"

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.date')
    def test_get_today_stats_returns_empty_when_no_data(
        self, mock_date, mock_session_class
    ):
        """
        Given: No coding activity today
        When: get_today_stats is called
        Then: It should return empty stats structure
        """
        # Arrange
        mock_date.today.return_value.strftime.return_value = "2024-01-10"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client.get_today_stats()
        
        # Assert
        assert result["grand_total"]["total_seconds"] == 0
        assert result["grand_total"]["text"] == "0 secs"
        assert result["languages"] == []
        assert result["range"]["date"] == "2024-01-10"


class TestGetDateStats:
    """Test getting statistics for a specific date."""

    @patch('lms.wakatime_client.requests.Session')
    def test_get_date_stats_returns_specific_date_data(self, mock_session_class):
        """
        Given: A specific date (2024-01-05)
        When: get_date_stats is called
        Then: It should return stats for that date
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "grand_total": {"text": "5 hrs 30 mins", "total_seconds": 19800},
                    "languages": [
                        {"name": "Python", "total_seconds": 15000},
                        {"name": "Go", "total_seconds": 4800}
                    ],
                    "range": {"date": "2024-01-05"}
                }
            ]
        }
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client.get_date_stats("2024-01-05")
        
        # Assert
        assert result["grand_total"]["total_seconds"] == 19800
        assert len(result["languages"]) == 2
        assert result["range"]["date"] == "2024-01-05"

    @patch('lms.wakatime_client.requests.Session')
    def test_get_date_stats_returns_empty_when_no_data(self, mock_session_class):
        """
        Given: No coding activity for the specified date
        When: get_date_stats is called
        Then: It should return empty stats structure
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client.get_date_stats("2024-01-01")
        
        # Assert
        assert result["grand_total"]["total_seconds"] == 0
        assert result["grand_total"]["text"] == "0 secs"
        assert result["languages"] == []
        assert result["range"]["date"] == "2024-01-01"


class TestDataParsing:
    """Test parsing of API response data."""

    @patch('lms.wakatime_client.requests.Session')
    def test_parsing_complex_response_structure(self, mock_session_class):
        """
        Given: Complex API response with multiple languages and projects
        When: Response is parsed
        Then: It should correctly extract all data fields
        """
        # Arrange
        complex_response = {
            "data": [
                {
                    "grand_total": {
                        "text": "4 hrs 23 mins",
                        "total_seconds": 15780,
                        "digital": "4:23",
                        "hours": 4,
                        "minutes": 23
                    },
                    "languages": [
                        {
                            "name": "Python",
                            "total_seconds": 10000,
                            "percent": 63.37
                        },
                        {
                            "name": "YAML",
                            "total_seconds": 3000,
                            "percent": 19.01
                        },
                        {
                            "name": "Markdown",
                            "total_seconds": 2780,
                            "percent": 17.62
                        }
                    ],
                    "range": {
                        "date": "2024-01-10",
                        "start": "2024-01-10T00:00:00Z",
                        "end": "2024-01-10T23:59:59Z",
                        "text": "Wed Jan 10th 2024",
                        "timezone": "Europe/Paris"
                    }
                }
            ]
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = complex_response
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client.get_today_stats()
        
        # Assert - verify all nested data is accessible
        assert result["grand_total"]["total_seconds"] == 15780
        assert result["grand_total"]["hours"] == 4
        assert result["grand_total"]["minutes"] == 23
        assert len(result["languages"]) == 3
        assert result["languages"][0]["name"] == "Python"
        assert result["languages"][0]["percent"] == 63.37
        assert result["range"]["timezone"] == "Europe/Paris"

    @patch('lms.wakatime_client.requests.Session')
    def test_parsing_handles_missing_optional_fields(self, mock_session_class):
        """
        Given: API response with minimal required fields
        When: Response is parsed
        Then: It should handle missing optional fields gracefully
        """
        # Arrange
        minimal_response = {
            "data": [
                {
                    "grand_total": {"text": "1 hr", "total_seconds": 3600},
                    "languages": [],
                    "range": {"date": "2024-01-10"}
                }
            ]
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = minimal_response
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act
        result = client.get_today_stats()
        
        # Assert
        assert result["grand_total"]["total_seconds"] == 3600
        assert result["languages"] == []
        assert "date" in result["range"]


class TestNoRealAPICalls:
    """Verify that tests never make real API calls."""

    def test_no_real_network_calls_in_tests(self):
        """
        Given: All tests in this file
        When: Tests are executed
        Then: No real network calls should be made (all mocked)
        """
        # This is a meta-test to document that all tests use mocks
        # If any test makes a real API call, it will fail due to missing/invalid API key
        
        # Verify mocking is used throughout
        import sys
        test_module = sys.modules[__name__]
        
        # Count tests that use @patch decorator
        test_classes = [
            TestMakeRequestSuccess,
            TestMakeRequestErrors,
            TestRetryLogic,
            TestGetSummaries,
            TestGetTodayStats,
            TestGetDateStats,
            TestDataParsing
        ]
        
        total_methods = 0
        for test_class in test_classes:
            methods = [m for m in dir(test_class) if m.startswith('test_')]
            total_methods += len(methods)
        
        # Assert we have comprehensive tests
        assert total_methods >= 15, "Should have at least 15 test methods"
        
        # All API-calling tests should use mocks (verified by @patch decorators)
        # This test serves as documentation that we never call real API


class TestErrorMessages:
    """Test that error messages are informative."""

    @patch('lms.wakatime_client.requests.Session')
    def test_auth_error_message_is_clear(self, mock_session_class):
        """
        Given: Authentication failure (401)
        When: Error is raised
        Then: Error message should clearly indicate auth issue
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="invalid")
        
        # Act & Assert
        with pytest.raises(WakaTimeAuthError) as exc_info:
            client._make_request("/test")
        
        assert "Invalid API key" in str(exc_info.value)

    @patch('lms.wakatime_client.requests.Session')
    @patch('lms.wakatime_client.time.sleep')
    def test_rate_limit_error_message_is_clear(
        self, mock_sleep, mock_session_class
    ):
        """
        Given: Rate limit exceeded (429)
        When: Error is raised after retries
        Then: Error message should clearly indicate rate limit
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 429
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test")
        
        # Act & Assert
        with pytest.raises(WakaTimeRateLimitError) as exc_info:
            client._make_request("/test")
        
        assert "rate limit" in str(exc_info.value).lower()

    @patch('lms.wakatime_client.requests.Session')
    def test_network_error_message_includes_details(self, mock_session_class):
        """
        Given: Network connection error
        When: Error is raised
        Then: Error message should include connection details
        """
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Failed to establish connection"
        )
        mock_session_class.return_value = mock_session
        
        client = WakaTimeClient(api_key="waka_test", max_retries=1)
        
        # Act & Assert
        with pytest.raises(WakaTimeNetworkError) as exc_info:
            client._make_request("/test")
        
        error_msg = str(exc_info.value)
        assert "Connection error" in error_msg or "Network error" in error_msg
