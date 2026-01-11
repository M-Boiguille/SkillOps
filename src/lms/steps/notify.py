"""Notification step - send daily report to Telegram."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from src.lms.integrations.telegram_client import TelegramClient
from src.lms.persistence import ProgressManager
from src.lms.steps.review import calculate_metrics_from_progress

console = Console()


def get_storage_path() -> Path:
    """Return storage path from environment or default location."""
    storage_path_str = os.getenv(
        "STORAGE_PATH", str(Path.home() / ".local/share/skillops")
    )
    return Path(storage_path_str).expanduser().absolute()


def should_send_now(schedule_time: str, now: Optional[datetime] = None) -> bool:
    """Check if current time matches the configured schedule (HH:MM)."""
    if not schedule_time:
        return True
    current = (now or datetime.now()).strftime("%H:%M")
    return current == schedule_time


def format_daily_report(date_str: str, metrics: dict, progress: dict) -> str:
    """Build a concise Markdown report for Telegram."""
    steps_completed = metrics.get("steps_completed", 0)
    total_time = metrics.get("total_time", 0)
    cards_created = metrics.get("cards_created", 0)
    streak = metrics.get("streak", 0)

    hours = total_time // 3600
    minutes = (total_time % 3600) // 60

    lines = [
        f"**SkillOps - Daily Summary {date_str}**",
        f"• Steps completed : {steps_completed}/8",
        f"• Time coded : {hours}h {minutes:02d}min",
        f"• Cards created : {cards_created}",
        f"• Streak : {streak} days",
    ]

    alerts = []
    if steps_completed < 6:
        alerts.append("⚠️ Day incomplete (<6 steps)")
    if total_time < 3600:
        alerts.append("⚠️ Low coding time (<1h)")

    if alerts:
        lines.append("\n".join(alerts))

    return "\n".join(lines)


def notify_step(
    storage_path: Optional[Path] = None, respect_schedule: bool = False
) -> bool:
    """Send today's progress summary to Telegram.

    Args:
        storage_path: Optional custom storage directory.
        respect_schedule: If True, only send at TELEGRAM_SCHEDULE_TIME.

    Returns:
        True if the notification was sent successfully, False otherwise.
    """
    console.print("\n[bold cyan]Notify - Telegram[/bold cyan]\n")

    schedule_time = os.getenv("TELEGRAM_SCHEDULE_TIME", "20:00").strip()
    if respect_schedule and not should_send_now(schedule_time):
        console.print(
            f"[yellow]Notification skipped (scheduled for {schedule_time}).[/yellow]\n"
        )
        return False

    storage_dir = storage_path or get_storage_path()
    progress_file = storage_dir / "progress.json"

    progress_manager = ProgressManager(progress_file)
    all_progress = progress_manager.load_progress()
    today_date = progress_manager.get_today_date()
    today_progress = progress_manager.get_progress_by_date(today_date)

    if not today_progress:
        console.print(
            "[yellow]No data for today. Complete steps before sending the notification.[/yellow]\n"
        )
        return False

    metrics = calculate_metrics_from_progress(today_progress, all_progress)
    report = format_daily_report(today_date, metrics, today_progress)

    try:
        client = TelegramClient.from_env()
    except ValueError as exc:  # Missing configuration
        console.print(f"[red]{exc}[/red]\n")
        return False

    try:
        sent = client.send_message(report)
    except Exception as exc:  # Network/API error
        console.print(f"[red]Telegram send failed: {exc}[/red]\n")
        return False

    if sent:
        console.print("[green]Telegram notification sent successfully![/green]\n")
    else:
        console.print("[red]Telegram send failed (response not ok).[/red]\n")

    return sent
