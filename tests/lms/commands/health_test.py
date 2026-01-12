"""Tests for health check command."""

from unittest.mock import MagicMock, patch

import requests
from src.lms.commands.health import (
    check_api_token,
    check_directory,
    check_github_token,
    check_telegram_token,
    health_check,
    is_fine_grained_github_token,
)


class TestCheckApiToken:
    """Tests for check_api_token function."""

    def test_check_api_token_present(self):
        """Test check_api_token returns True when token is set."""
        with patch.dict("os.environ", {"TEST_TOKEN": "test-value"}):
            result = check_api_token("Test", "TEST_TOKEN")
            assert result is True

    def test_check_api_token_missing(self):
        """Test check_api_token returns False when token is not set."""
        with patch.dict("os.environ", {}, clear=True):
            result = check_api_token("Test", "MISSING_TOKEN")
            assert result is False

    def test_check_api_token_empty(self):
        """Test check_api_token returns False when token is empty string."""
        with patch.dict("os.environ", {"EMPTY_TOKEN": ""}):
            result = check_api_token("Test", "EMPTY_TOKEN")
            assert result is False

    def test_check_api_token_wakatime_format_invalid(self):
        """Invalid WakaTime format should fail the check."""
        with patch.dict("os.environ", {"WAKATIME_API_KEY": "invalid"}):
            result = check_api_token("WakaTime", "WAKATIME_API_KEY")
            assert result is False


class TestCheckGithubToken:
    """Tests for check_github_token function."""

    @patch("src.lms.commands.health.requests.get")
    def test_check_github_token_valid(self, mock_get):
        """Test check_github_token returns True with valid token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser"}
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"GITHUB_TOKEN": "valid-token"}):
            result = check_github_token()
            assert result is True
            mock_get.assert_called_once()

    @patch("src.lms.commands.health.requests.get")
    def test_check_github_token_invalid(self, mock_get):
        """Test check_github_token returns False with invalid token."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"GITHUB_TOKEN": "invalid-token"}):
            result = check_github_token()
            assert result is False

    def test_check_github_token_missing(self):
        """Test check_github_token returns False when token not set."""
        with patch.dict("os.environ", {}, clear=True):
            result = check_github_token()
            assert result is False

    def test_check_github_token_fine_grained_prefix(self):
        """Fine-grained token prefixes should be detected without error."""
        assert is_fine_grained_github_token("github_pat_abc") is True
        assert is_fine_grained_github_token("ghp_abc") is False

    @patch("src.lms.commands.health.requests.get")
    def test_check_github_token_network_error(self, mock_get):
        """Test check_github_token handles network errors gracefully."""
        mock_get.side_effect = requests.RequestException("Connection timeout")

        with patch.dict("os.environ", {"GITHUB_TOKEN": "valid-token"}):
            result = check_github_token()
            assert result is False


class TestCheckTelegramToken:
    """Tests for check_telegram_token function."""

    @patch("src.lms.commands.health.requests.get")
    def test_check_telegram_token_valid(self, mock_get):
        """Test check_telegram_token returns True with valid token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": True,
            "result": {"first_name": "TestBot"},
        }
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "valid-token"}):
            result = check_telegram_token()
            assert result is True

    @patch("src.lms.commands.health.requests.get")
    def test_check_telegram_token_invalid(self, mock_get):
        """Test check_telegram_token returns False with invalid token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": False}
        mock_get.return_value = mock_response

        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "invalid-token"}):
            result = check_telegram_token()
            assert result is False

    def test_check_telegram_token_missing(self):
        """Test check_telegram_token returns False when token not set."""
        with patch.dict("os.environ", {}, clear=True):
            result = check_telegram_token()
            assert result is False

    @patch("src.lms.commands.health.requests.get")
    def test_check_telegram_token_network_error(self, mock_get):
        """Test check_telegram_token handles network errors gracefully."""
        mock_get.side_effect = requests.RequestException("Connection timeout")

        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "valid-token"}):
            result = check_telegram_token()
            assert result is False


class TestCheckDirectory:
    """Tests for check_directory function."""

    def test_check_directory_exists(self, tmp_path):
        """Test check_directory returns True when directory exists."""
        with patch.dict("os.environ", {"TEST_DIR": str(tmp_path)}):
            result = check_directory("Test", "TEST_DIR")
            assert result is True

    def test_check_directory_missing(self, tmp_path):
        """Test check_directory returns False when directory missing."""
        missing_path = tmp_path / "nonexistent"
        with patch.dict("os.environ", {"TEST_DIR": str(missing_path)}):
            result = check_directory("Test", "TEST_DIR")
            assert result is False

    def test_check_directory_with_default(self, tmp_path):
        """Test check_directory uses default path when env var not set."""
        with patch.dict("os.environ", {}, clear=True):
            result = check_directory("Test", "UNSET_DIR", default=tmp_path)
            assert result is True

    def test_check_directory_env_overrides_default(self, tmp_path):
        """Test check_directory prefers env var over default."""
        custom_path = tmp_path / "custom"
        custom_path.mkdir()
        default_path = tmp_path / "default"
        default_path.mkdir()

        with patch.dict("os.environ", {"TEST_DIR": str(custom_path)}):
            result = check_directory("Test", "TEST_DIR", default=default_path)
            assert result is True


class TestHealthCheck:
    """Tests for health_check function."""

    @patch("src.lms.commands.health.check_telegram_token")
    @patch("src.lms.commands.health.check_github_token")
    @patch("src.lms.commands.health.check_directory")
    @patch("src.lms.commands.health.check_api_token")
    def test_health_check_all_healthy(
        self, mock_api_token, mock_directory, mock_github, mock_telegram
    ):
        """Test health_check returns True when all components healthy."""
        mock_api_token.return_value = True
        mock_github.return_value = True
        mock_telegram.return_value = True
        mock_directory.return_value = True

        with patch.dict(
            "os.environ",
            {
                "WAKATIME_API_KEY": "key1",
                "GEMINI_API_KEY": "key2",
                "GITHUB_TOKEN": "key3",
                "TELEGRAM_BOT_TOKEN": "key4",
            },
        ):
            result = health_check()
            assert result is True

    @patch("src.lms.commands.health.check_telegram_token")
    @patch("src.lms.commands.health.check_github_token")
    @patch("src.lms.commands.health.check_directory")
    @patch("src.lms.commands.health.check_api_token")
    def test_health_check_missing_token(
        self, mock_api_token, mock_directory, mock_github, mock_telegram
    ):
        """Test health_check returns False when critical token missing."""
        # First few tokens pass, then one fails
        mock_api_token.side_effect = [True, True, True, False]
        mock_github.return_value = True
        mock_telegram.return_value = True
        mock_directory.return_value = True

        with patch.dict("os.environ", {}):
            result = health_check()
            assert result is False

    @patch("src.lms.commands.health.check_telegram_token")
    @patch("src.lms.commands.health.check_github_token")
    @patch("src.lms.commands.health.check_directory")
    @patch("src.lms.commands.health.check_api_token")
    def test_health_check_api_failure(
        self, mock_api_token, mock_directory, mock_github, mock_telegram
    ):
        """Test health_check returns False when GitHub API check fails."""
        mock_api_token.return_value = True
        mock_github.return_value = False
        mock_telegram.return_value = True
        mock_directory.return_value = True

        with patch.dict("os.environ", {}):
            result = health_check()
            assert result is False

    @patch("src.lms.commands.health.check_telegram_token")
    @patch("src.lms.commands.health.check_github_token")
    @patch("src.lms.commands.health.check_directory")
    @patch("src.lms.commands.health.check_api_token")
    def test_health_check_missing_directory(
        self, mock_api_token, mock_directory, mock_github, mock_telegram
    ):
        """Test health_check returns False when critical directory missing."""
        mock_api_token.return_value = True
        mock_github.return_value = True
        mock_telegram.return_value = True
        # Storage passes, Labs fails, Obsidian not checked (env var not set)
        mock_directory.side_effect = [True, False]

        with patch.dict("os.environ", {}, clear=True):
            result = health_check()
            assert result is False
