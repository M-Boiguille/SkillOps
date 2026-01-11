"""Tests for custom exception classes."""

import pytest

from src.lms.exceptions import (
    AnkiError,
    GeminiError,
    GitHubAuthError,
    GitHubPushError,
    GitHubRepositoryError,
    ObsidianError,
    SkillOpsError,
    TelegramError,
    WakaTimeError,
)


class TestSkillOpsError:
    """Test base SkillOpsError class."""

    def test_skillops_error_with_message_only(self) -> None:
        """Test creating error with message only."""
        error = SkillOpsError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.hint is None

    def test_skillops_error_with_message_and_hint(self) -> None:
        """Test creating error with message and hint."""
        error = SkillOpsError("Something failed", "Try restarting")
        assert "Something failed" in str(error)
        assert "💡 Hint: Try restarting" in str(error)
        assert error.message == "Something failed"
        assert error.hint == "Try restarting"

    def test_skillops_error_inheritance(self) -> None:
        """Test that SkillOpsError inherits from Exception."""
        error = SkillOpsError("Test error")
        assert isinstance(error, Exception)

    def test_skillops_error_can_be_raised_and_caught(self) -> None:
        """Test that SkillOpsError can be raised and caught."""
        with pytest.raises(SkillOpsError) as exc_info:
            raise SkillOpsError("Test error")
        assert exc_info.value.message == "Test error"


class TestGitHubAuthError:
    """Test GitHub authentication error."""

    def test_github_auth_error_default_message(self) -> None:
        """Test default message for GitHub auth error."""
        error = GitHubAuthError()
        assert "GitHub authentication failed" in str(error)
        assert "Check your GitHub token" in str(error)

    def test_github_auth_error_custom_message(self) -> None:
        """Test custom message for GitHub auth error."""
        error = GitHubAuthError("Token expired")
        assert "Token expired" in str(error)
        assert "Check your GitHub token" in str(error)

    def test_github_auth_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = GitHubAuthError()
        error_str = str(error)
        assert "repo" in error_str
        assert "scope" in error_str
        assert "github.com/settings/tokens" in error_str

    def test_github_auth_error_can_be_caught(self) -> None:
        """Test GitHub auth error can be caught."""
        with pytest.raises(GitHubAuthError):
            raise GitHubAuthError("Invalid token")


class TestGitHubRepositoryError:
    """Test GitHub repository operation error."""

    def test_github_repository_error_default_message(self) -> None:
        """Test default message for GitHub repository error."""
        error = GitHubRepositoryError()
        assert "GitHub repository operation failed" in str(error)
        assert "permissions" in str(error)

    def test_github_repository_error_custom_message(self) -> None:
        """Test custom message for GitHub repository error."""
        error = GitHubRepositoryError("Repo already exists")
        assert "Repo already exists" in str(error)

    def test_github_repository_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = GitHubRepositoryError()
        error_str = str(error)
        assert "permissions" in error_str
        assert "rate_limit" in error_str
        assert "api.github.com" in error_str

    def test_github_repository_error_can_be_caught(self) -> None:
        """Test GitHub repository error can be caught."""
        with pytest.raises(GitHubRepositoryError):
            raise GitHubRepositoryError()


class TestGitHubPushError:
    """Test GitHub push operation error."""

    def test_github_push_error_default_message(self) -> None:
        """Test default message for GitHub push error."""
        error = GitHubPushError()
        assert "Push to GitHub failed" in str(error)
        assert "network" in str(error)

    def test_github_push_error_custom_message(self) -> None:
        """Test custom message for GitHub push error."""
        error = GitHubPushError("Connection timeout")
        assert "Connection timeout" in str(error)

    def test_github_push_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = GitHubPushError()
        error_str = str(error)
        assert "connectivity" in error_str
        assert "git config" in error_str
        assert "github.com" in error_str

    def test_github_push_error_can_be_caught(self) -> None:
        """Test GitHub push error can be caught."""
        with pytest.raises(GitHubPushError):
            raise GitHubPushError()


class TestTelegramError:
    """Test Telegram API error."""

    def test_telegram_error_default_message(self) -> None:
        """Test default message for Telegram error."""
        error = TelegramError()
        assert "Telegram API error" in str(error)
        assert "token" in str(error).lower()

    def test_telegram_error_custom_message(self) -> None:
        """Test custom message for Telegram error."""
        error = TelegramError("Bot token invalid")
        assert "Bot token invalid" in str(error)

    def test_telegram_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = TelegramError()
        error_str = str(error)
        assert "BotFather" in error_str
        assert "token" in error_str.lower()
        assert "telegram.org" in error_str

    def test_telegram_error_can_be_caught(self) -> None:
        """Test Telegram error can be caught."""
        with pytest.raises(TelegramError):
            raise TelegramError()


class TestObsidianError:
    """Test Obsidian vault error."""

    def test_obsidian_error_default_message(self) -> None:
        """Test default message for Obsidian error."""
        error = ObsidianError()
        assert "Obsidian vault error" in str(error)
        assert "path" in str(error)

    def test_obsidian_error_custom_message(self) -> None:
        """Test custom message for Obsidian error."""
        error = ObsidianError("Vault not found")
        assert "Vault not found" in str(error)

    def test_obsidian_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = ObsidianError()
        error_str = str(error)
        assert "OBSIDIAN_VAULT_PATH" in error_str
        assert "permissions" in error_str
        assert "chmod" in error_str

    def test_obsidian_error_can_be_caught(self) -> None:
        """Test Obsidian error can be caught."""
        with pytest.raises(ObsidianError):
            raise ObsidianError()


class TestAnkiError:
    """Test Anki sync error."""

    def test_anki_error_default_message(self) -> None:
        """Test default message for Anki error."""
        error = AnkiError()
        assert "Anki sync failed" in str(error)
        assert "AnkiConnect" in str(error)

    def test_anki_error_custom_message(self) -> None:
        """Test custom message for Anki error."""
        error = AnkiError("Sync timeout")
        assert "Sync timeout" in str(error)

    def test_anki_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = AnkiError()
        error_str = str(error)
        assert "AnkiConnect" in error_str
        assert "8765" in error_str
        assert "apkg" in error_str

    def test_anki_error_can_be_caught(self) -> None:
        """Test Anki error can be caught."""
        with pytest.raises(AnkiError):
            raise AnkiError()


class TestWakaTimeError:
    """Test WakaTime API error."""

    def test_wakatime_error_default_message(self) -> None:
        """Test default message for WakaTime error."""
        error = WakaTimeError()
        assert "WakaTime API error" in str(error)
        assert "key" in str(error).lower()

    def test_wakatime_error_custom_message(self) -> None:
        """Test custom message for WakaTime error."""
        error = WakaTimeError("Invalid API key")
        assert "Invalid API key" in str(error)

    def test_wakatime_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = WakaTimeError()
        error_str = str(error)
        assert "WAKATIME_API_KEY" in error_str
        assert "wakatime.com" in error_str
        assert "editor" in error_str

    def test_wakatime_error_can_be_caught(self) -> None:
        """Test WakaTime error can be caught."""
        with pytest.raises(WakaTimeError):
            raise WakaTimeError()


class TestGeminiError:
    """Test Gemini API error."""

    def test_gemini_error_default_message(self) -> None:
        """Test default message for Gemini error."""
        error = GeminiError()
        assert "Gemini API error" in str(error)
        assert "key" in str(error).lower()

    def test_gemini_error_custom_message(self) -> None:
        """Test custom message for Gemini error."""
        error = GeminiError("API quota exceeded")
        assert "API quota exceeded" in str(error)

    def test_gemini_error_has_helpful_hints(self) -> None:
        """Test that error contains helpful hints."""
        error = GeminiError()
        error_str = str(error)
        assert "GEMINI_API_KEY" in error_str
        assert "makersuite.google.com" in error_str
        assert "quota" in error_str

    def test_gemini_error_can_be_caught(self) -> None:
        """Test Gemini error can be caught."""
        with pytest.raises(GeminiError):
            raise GeminiError()


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_all_custom_exceptions_inherit_from_skillops_error(self) -> None:
        """Test that all custom exceptions inherit from SkillOpsError."""
        exceptions = [
            GitHubAuthError,
            GitHubRepositoryError,
            GitHubPushError,
            TelegramError,
            ObsidianError,
            AnkiError,
            WakaTimeError,
            GeminiError,
        ]
        for exc_class in exceptions:
            error = exc_class()
            assert isinstance(error, SkillOpsError)
            assert isinstance(error, Exception)

    def test_exception_can_catch_parent_type(self) -> None:
        """Test that specific exceptions can be caught as SkillOpsError."""
        with pytest.raises(SkillOpsError):
            raise GitHubAuthError("Test")

        with pytest.raises(SkillOpsError):
            raise TelegramError("Test")

        with pytest.raises(SkillOpsError):
            raise AnkiError("Test")
