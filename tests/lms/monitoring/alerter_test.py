"""Tests for alerting modules."""

from unittest.mock import MagicMock, patch

import requests
from src.lms.monitoring.alerter import (
    EmailAlerter,
    WebhookAlerter,
    send_alert_from_aggregator,
)
from src.lms.monitoring.error_aggregator import ErrorAggregator


class TestEmailAlerter:
    """Tests for email alerting."""

    def test_email_alerter_initialization(self):
        """Test email alerter setup."""
        alerter = EmailAlerter(
            smtp_host="smtp.example.com",
            from_address="alerts@example.com",
        )

        assert alerter.smtp_host == "smtp.example.com"
        assert alerter.from_address == "alerts@example.com"
        assert alerter.smtp_port == 25

    @patch.dict(
        "os.environ",
        {
            "SKILLOPS_ALERT_SMTP_HOST": "mail.example.com",
            "SKILLOPS_ALERT_SMTP_PORT": "587",
            "SKILLOPS_ALERT_FROM": "ops@example.com",
        },
    )
    def test_email_alerter_from_env(self):
        """Test email alerter uses environment variables."""
        alerter = EmailAlerter()

        assert alerter.smtp_host == "mail.example.com"
        assert alerter.smtp_port == 587
        assert alerter.from_address == "ops@example.com"

    def test_format_error_summary(self):
        """Test error summary formatting."""
        alerter = EmailAlerter()
        summary = {
            "create": {
                "count": 2,
                "types": ["ValueError", "TypeError"],
                "sample_message": "Invalid input",
            },
            "share": {
                "count": 1,
                "types": ["GitHubError"],
                "sample_message": "API rate limit exceeded",
            },
        }

        html = alerter._format_error_summary(summary)

        assert "create" in html
        assert "share" in html
        assert "2" in html  # error count
        assert "ValueError" in html
        assert "journalctl" in html

    @patch("smtplib.SMTP")
    def test_send_email_alert_localhost(self, mock_smtp):
        """Test sending email via localhost SMTP."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        alerter = EmailAlerter()
        summary = {
            "create": {
                "count": 1,
                "types": ["Error"],
                "sample_message": "Test error",
            }
        }

        result = alerter.send_alert(
            "Test Alert",
            summary,
            recipients=["admin@example.com"],
        )

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_email_alert_authenticated(self, mock_smtp):
        """Test sending email with SMTP authentication."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        alerter = EmailAlerter(
            username="user@example.com",
            password="secret",
        )
        summary = {"test": {"count": 1, "types": ["Error"], "sample_message": ""}}

        result = alerter.send_alert(
            "Test",
            summary,
            recipients=["admin@example.com"],
        )

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "secret")

    @patch.dict(
        "os.environ", {"SKILLOPS_ALERT_RECIPIENTS": "admin@example.com,ops@example.com"}
    )
    @patch("smtplib.SMTP")
    def test_send_email_alert_from_env(self, mock_smtp):
        """Test email recipients from environment variable."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        alerter = EmailAlerter()
        result = alerter.send_alert(
            "Test", {"step": {"count": 1, "types": [], "sample_message": ""}}
        )

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_email_no_recipients(self, mock_smtp):
        """Test email alert with no recipients specified."""
        alerter = EmailAlerter()
        summary = {"test": {"count": 1, "types": ["Error"], "sample_message": ""}}

        result = alerter.send_alert("Test", summary, recipients=[])

        assert result is False
        mock_smtp.assert_not_called()

    @patch("smtplib.SMTP")
    def test_send_email_smtp_error(self, mock_smtp):
        """Test handling of SMTP errors."""
        import smtplib

        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

        alerter = EmailAlerter()
        summary = {"test": {"count": 1, "types": ["Error"], "sample_message": ""}}

        result = alerter.send_alert(
            "Test",
            summary,
            recipients=["admin@example.com"],
        )

        assert result is False


class TestWebhookAlerter:
    """Tests for webhook alerting."""

    def test_webhook_alerter_initialization(self):
        """Test webhook alerter setup."""
        alerter = WebhookAlerter(webhook_url="https://hooks.example.com/alerting")

        assert alerter.webhook_url == "https://hooks.example.com/alerting"

    @patch.dict(
        "os.environ",
        {"SKILLOPS_ALERT_WEBHOOK_URL": "https://hooks.slack.com/services/123"},
    )
    def test_webhook_alerter_from_env(self):
        """Test webhook alerter uses environment variable."""
        alerter = WebhookAlerter()

        assert alerter.webhook_url == "https://hooks.slack.com/services/123"

    def test_format_slack_message(self):
        """Test Slack message formatting."""
        alerter = WebhookAlerter()
        summary = {
            "create": {
                "count": 2,
                "types": ["ValueError"],
                "sample_message": "Invalid input",
            }
        }

        payload = alerter._format_slack_message("Test Alert", summary)

        assert "blocks" in payload
        assert len(payload["blocks"]) >= 2
        assert payload["blocks"][0]["type"] == "section"

    def test_format_webhook_message_empty(self):
        """Test formatting with empty error summary."""
        alerter = WebhookAlerter()

        payload = alerter._format_slack_message("Test Alert", {})

        assert "blocks" in payload
        assert payload["blocks"][0]["text"]["text"] == "*Test Alert*"

    @patch("requests.post")
    def test_send_webhook_alert(self, mock_post):
        """Test sending webhook alert."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        alerter = WebhookAlerter(webhook_url="https://hooks.example.com")
        summary = {
            "create": {
                "count": 1,
                "types": ["Error"],
                "sample_message": "Test",
            }
        }

        result = alerter.send_alert("Alert", summary)

        assert result is True
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.example.com"
        assert "json" in call_args[1]

    @patch("requests.post")
    def test_send_webhook_alert_failure(self, mock_post):
        """Test webhook alert handling non-200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        alerter = WebhookAlerter(webhook_url="https://hooks.example.com")
        summary = {
            "create": {
                "count": 1,
                "types": ["Error"],
                "sample_message": "Test",
            }
        }

        result = alerter.send_alert("Alert", summary)

        assert result is False

    @patch("requests.post")
    def test_send_webhook_no_url(self, mock_post):
        """Test webhook alert with no URL configured."""
        alerter = WebhookAlerter()
        summary = {
            "create": {
                "count": 1,
                "types": ["Error"],
                "sample_message": "Test",
            }
        }

        result = alerter.send_alert("Alert", summary)

        assert result is False
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_send_webhook_network_error(self, mock_post):
        """Test webhook alert handling network errors."""
        mock_post.side_effect = requests.RequestException("Connection timeout")

        alerter = WebhookAlerter(webhook_url="https://hooks.example.com")
        summary = {
            "create": {
                "count": 1,
                "types": ["Error"],
                "sample_message": "Test",
            }
        }

        result = alerter.send_alert("Alert", summary)

        assert result is False


class TestSendAlertFromAggregator:
    """Tests for convenience function."""

    def test_send_alert_from_aggregator_no_errors(self, tmp_path):
        """Test alert when no errors recorded."""
        aggregator = ErrorAggregator(storage_path=tmp_path)

        result = send_alert_from_aggregator(aggregator)

        assert result is False

    @patch("src.lms.monitoring.alerter.EmailAlerter.send_alert")
    def test_send_alert_from_aggregator_email(self, mock_send, tmp_path):
        """Test sending email alert from aggregator."""
        mock_send.return_value = True

        aggregator = ErrorAggregator(storage_path=tmp_path)
        aggregator.record_error(ValueError("Test"), step_id="create")

        result = send_alert_from_aggregator(aggregator, alert_type="email")

        assert result is True
        mock_send.assert_called_once()

    @patch("src.lms.monitoring.alerter.WebhookAlerter.send_alert")
    def test_send_alert_from_aggregator_webhook(self, mock_send, tmp_path):
        """Test sending webhook alert from aggregator."""
        mock_send.return_value = True

        aggregator = ErrorAggregator(storage_path=tmp_path)
        aggregator.record_error(ValueError("Test"), step_id="create")

        result = send_alert_from_aggregator(aggregator, alert_type="webhook")

        assert result is True
        mock_send.assert_called_once()

    @patch("src.lms.monitoring.alerter.EmailAlerter.send_alert")
    @patch("src.lms.monitoring.alerter.WebhookAlerter.send_alert")
    def test_send_alert_from_aggregator_both(self, mock_webhook, mock_email, tmp_path):
        """Test sending both email and webhook alerts."""
        mock_email.return_value = True
        mock_webhook.return_value = True

        aggregator = ErrorAggregator(storage_path=tmp_path)
        aggregator.record_error(ValueError("Test"), step_id="create")

        result = send_alert_from_aggregator(aggregator, alert_type="both")

        assert result is True
        mock_email.assert_called_once()
        mock_webhook.assert_called_once()
