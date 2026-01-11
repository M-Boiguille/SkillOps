"""Alerting system for SkillOps monitoring (email, webhooks, Slack)."""

from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
from src.lms.monitoring.error_aggregator import ErrorAggregator


class EmailAlerter:
    """Send email alerts for critical errors and metrics."""

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 25,
        from_address: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize email alerter.

        Args:
            smtp_host: SMTP server hostname (default localhost)
            smtp_port: SMTP server port (default 25 for unauth)
            from_address: Sender email address
            username: SMTP username (optional)
            password: SMTP password (optional)

        Environment Variables:
            SKILLOPS_ALERT_FROM: Sender email address
            SKILLOPS_ALERT_SMTP_HOST: SMTP hostname
            SKILLOPS_ALERT_SMTP_PORT: SMTP port
            SKILLOPS_ALERT_SMTP_USER: SMTP username
            SKILLOPS_ALERT_SMTP_PASS: SMTP password
        """
        self.smtp_host = os.getenv("SKILLOPS_ALERT_SMTP_HOST", smtp_host)
        self.smtp_port = int(os.getenv("SKILLOPS_ALERT_SMTP_PORT", str(smtp_port)))
        self.from_address = (
            os.getenv("SKILLOPS_ALERT_FROM") or from_address or "skillops@localhost"
        )
        self.username = os.getenv("SKILLOPS_ALERT_SMTP_USER", username)
        self.password = os.getenv("SKILLOPS_ALERT_SMTP_PASS", password)

    def _format_error_summary(self, summary: Dict[str, Dict[str, Any]]) -> str:
        """Format error summary as HTML email body."""
        html_parts = [
            "<h2>SkillOps Monitoring Alert</h2>",
            "<p>Critical errors detected in the past 24 hours.</p>",
            "<table border='1' cellpadding='10'>",
            "<tr><th>Step</th><th>Error Count</th><th>Types</th>",
            "<th>Latest Message</th></tr>",
        ]

        for step_id, error_info in summary.items():
            count = error_info.get("count", 0)
            types = ", ".join(error_info.get("types", []))
            message = error_info.get("sample_message", "")

            html_parts.append(
                f"<tr>"
                f"<td>{step_id}</td>"
                f"<td>{count}</td>"
                f"<td>{types}</td>"
                f"<td>{message[:100]}</td>"
                f"</tr>"
            )

        html_parts.append("</table>")
        html_parts.append("<p><em>Review logs with: journalctl -u skillops</em></p>")

        return "\n".join(html_parts)

    def send_alert(
        self,
        subject: str,
        errors: Dict[str, Any],
        recipients: Optional[List[str]] = None,
    ) -> bool:
        """Send email alert with error summary.

        Args:
            subject: Email subject line
            errors: Error summary dict from ErrorAggregator.get_summary_by_step()
            recipients: Email addresses to send to
                       (default reads SKILLOPS_ALERT_RECIPIENTS env var)

        Returns:
            True if email sent successfully, False otherwise

        Environment Variables:
            SKILLOPS_ALERT_RECIPIENTS: Comma-separated list of recipients
        """
        if recipients is None:
            recipients_str = os.getenv("SKILLOPS_ALERT_RECIPIENTS", "")
            recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]

        if not recipients:
            return False

        try:
            # Build email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_address
            msg["To"] = ", ".join(recipients)

            # Text and HTML versions
            text_part = MIMEText(
                f"{subject}\n\nError Summary:\n"
                f"{errors}\n\nReview logs: journalctl -u skillops"
            )
            html_part = MIMEText(self._format_error_summary(errors), "html")

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            if self.username and self.password:
                # Authenticated SMTP
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                # Anonymous SMTP (localhost postfix, etc)
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.send_message(msg)

            return True

        except (smtplib.SMTPException, OSError) as e:
            # Log error but don't crash
            print(
                f"[ALERT] Failed to send email alert: {e}",
                flush=True,
            )
            return False


class WebhookAlerter:
    """Send webhook alerts (Slack, Discord, custom)."""

    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize webhook alerter.

        Args:
            webhook_url: Webhook URL (default reads env var)

        Environment Variables:
            SKILLOPS_ALERT_WEBHOOK_URL: Webhook endpoint
        """
        self.webhook_url = webhook_url or os.getenv("SKILLOPS_ALERT_WEBHOOK_URL", "")

    def _format_slack_message(
        self, subject: str, errors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format error summary for Slack webhook."""
        blocks: List[Dict[str, Any]] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{subject}*",
                },
            },
        ]

        # Add error summary as fields
        if errors:
            fields: List[Dict[str, str]] = []
            for step_id, error_info in errors.items():
                fields.append(
                    {
                        "type": "mrkdwn",
                        "text": f"*{step_id}*\n{error_info.get('count', 0)} "
                        f"errors\n_{error_info.get('sample_message', '')}_",
                    }
                )

            if fields:
                blocks.append(
                    {
                        "type": "section",
                        "fields": fields[:5],  # Slack limit
                    }
                )

        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "View logs: `journalctl -u skillops`",
                    }
                ],
            }
        )

        return {"blocks": blocks}

    def send_alert(
        self, subject: str, errors: Dict[str, Any], webhook_url: Optional[str] = None
    ) -> bool:
        """Send webhook alert.

        Args:
            subject: Alert title
            errors: Error summary dict
            webhook_url: Webhook URL override

        Returns:
            True if webhook sent successfully
        """
        url = webhook_url or self.webhook_url
        if not url:
            return False

        try:
            payload = self._format_slack_message(subject, errors)
            response = requests.post(
                url,
                json=payload,
                timeout=5,
            )
            return response.status_code == 200

        except requests.RequestException:
            return False


def send_alert_from_aggregator(
    aggregator: ErrorAggregator,
    alert_type: str = "email",
) -> bool:
    """Convenience function: send alert from error aggregator.

    Args:
        aggregator: ErrorAggregator instance
        alert_type: 'email', 'webhook', or 'both'

    Returns:
        True if at least one alert sent successfully
    """
    summary = aggregator.get_summary_by_step()
    if not summary:
        return False

    alerts_sent = False

    if alert_type in ("email", "both"):
        emailer = EmailAlerter()
        if emailer.send_alert(
            "SkillOps: Critical Errors Detected",
            summary,
        ):
            alerts_sent = True

    if alert_type in ("webhook", "both"):
        webhooker = WebhookAlerter()
        if webhooker.send_alert(
            "SkillOps: Critical Errors Detected",
            summary,
        ):
            alerts_sent = True

    return alerts_sent
