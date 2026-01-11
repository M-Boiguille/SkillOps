"""Custom exception classes for SkillOps LMS with helpful error messages."""

from typing import Optional


class SkillOpsError(Exception):
    """Base exception class for all SkillOps errors."""

    def __init__(self, message: str, hint: Optional[str] = None) -> None:
        """Initialize exception with message and optional hint.

        Args:
            message: The error message describing what went wrong.
            hint: Optional helpful hint on how to resolve the issue.
        """
        self.message = message
        self.hint = hint
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the complete error message with hint if available."""
        if self.hint:
            return f"{self.message}\n💡 Hint: {self.hint}"
        return self.message


class GitHubAuthError(SkillOpsError):
    """Raised when GitHub authentication fails."""

    def __init__(self, message: str = "GitHub authentication failed") -> None:
        """Initialize GitHub auth error with helpful hint."""
        hint = (
            "1. Check your GitHub token is valid: `echo $GITHUB_TOKEN`\n"
            "2. Token may have expired - create a new one at "
            "https://github.com/settings/tokens/new\n"
            "3. Ensure token has 'repo' scope"
        )
        super().__init__(message, hint)


class GitHubRepositoryError(SkillOpsError):
    """Raised when GitHub repository creation or access fails."""

    def __init__(self, message: str = "GitHub repository operation failed") -> None:
        """Initialize GitHub repository error with helpful hint."""
        hint = (
            "1. Check repository permissions (need 'repo' scope)\n"
            "2. Repository may already exist - try manually deleting it\n"
            "3. Check GitHub API rate limit: `curl -H "
            "'Authorization: token $GITHUB_TOKEN' "
            "https://api.github.com/rate_limit`"
        )
        super().__init__(message, hint)


class GitHubPushError(SkillOpsError):
    """Raised when pushing to GitHub fails."""

    def __init__(self, message: str = "Push to GitHub failed") -> None:
        """Initialize GitHub push error with helpful hint."""
        hint = (
            "1. Check network connectivity: `curl -I https://github.com`\n"
            "2. Git may need credentials configured: "
            "`git config --global user.name` and `git config --global user.email`\n"
            "3. Check SSH keys if using SSH: `ssh -T git@github.com`"
        )
        super().__init__(message, hint)


class TelegramError(SkillOpsError):
    """Raised when Telegram API operations fail."""

    def __init__(self, message: str = "Telegram API error") -> None:
        """Initialize Telegram error with helpful hint."""
        hint = (
            "1. Check your Telegram bot token is valid: `echo $TELEGRAM_BOT_TOKEN`\n"
            "2. Token may be invalid - create a new one with @BotFather\n"
            "3. Bot may be blocked or not started by the user\n"
            "4. Check Telegram API status: https://core.telegram.org/api/status"
        )
        super().__init__(message, hint)


class ObsidianError(SkillOpsError):
    """Raised when Obsidian vault operations fail."""

    def __init__(self, message: str = "Obsidian vault error") -> None:
        """Initialize Obsidian error with helpful hint."""
        hint = (
            "1. Check vault path is correct: `ls $OBSIDIAN_VAULT_PATH`\n"
            "2. Ensure vault exists and is readable: `ls -la $OBSIDIAN_VAULT_PATH`\n"
            "3. Check permissions: `chmod u+rw $OBSIDIAN_VAULT_PATH`\n"
            "4. Restart Obsidian to refresh file index"
        )
        super().__init__(message, hint)


class AnkiError(SkillOpsError):
    """Raised when Anki sync or import operations fail."""

    def __init__(self, message: str = "Anki sync failed") -> None:
        """Initialize Anki error with helpful hint."""
        hint = (
            "1. Check AnkiConnect is installed and running: "
            "https://github.com/FooSoft/anki-connect\n"
            "2. Ensure Anki is running with correct port (default 8765)\n"
            "3. Check deck format is valid (apkg or genanki format)\n"
            "4. Restart Anki and try again"
        )
        super().__init__(message, hint)


class WakaTimeError(SkillOpsError):
    """Raised when WakaTime API operations fail."""

    def __init__(self, message: str = "WakaTime API error") -> None:
        """Initialize WakaTime error with helpful hint."""
        hint = (
            "1. Check your WakaTime API key: `echo $WAKATIME_API_KEY`\n"
            "2. Get a new key from: https://wakatime.com/settings/api-key\n"
            "3. Ensure WakaTime extension is installed in your editor\n"
            "4. Check WakaTime status page: https://status.wakatime.com"
        )
        super().__init__(message, hint)


class GeminiError(SkillOpsError):
    """Raised when Gemini API operations fail."""

    def __init__(self, message: str = "Gemini API error") -> None:
        """Initialize Gemini error with helpful hint."""
        hint = (
            "1. Check your Gemini API key: `echo $GEMINI_API_KEY`\n"
            "2. Get a free key from: https://makersuite.google.com/app/apikey\n"
            "3. Verify API key has Generative Language API enabled\n"
            "4. Check quota: API key may have daily limits"
        )
        super().__init__(message, hint)
