"""Notification step - send daily report to Telegram."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from src.lms.integrations.telegram_client import TelegramClient
from src.lms.paths import get_storage_path
from src.lms.database import get_logical_date, init_db
from src.lms.persistence import (
    get_daily_summary,
    get_progress_history,
    calculate_streak,
)

console = Console()


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


def calculate_metrics_from_progress(
    today_progress: dict,
    history: list,
    storage_path: Optional[Path] = None,
) -> dict:
    """Compute daily metrics without legacy review step."""
    steps_completed = today_progress.get("steps_completed")
    if steps_completed is None:
        steps_completed = len(today_progress.get("steps_list", []) or [])

    total_minutes = today_progress.get("total_time_minutes", 0) or 0
    cards_created = today_progress.get("cards_created", 0) or 0
    streak = calculate_streak(storage_path=storage_path)

    return {
        "steps_completed": steps_completed,
        "total_time": total_minutes * 60,
        "cards_created": cards_created,
        "streak": streak,
        "history_size": len(history or []),
    }


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
    storage_dir.mkdir(parents=True, exist_ok=True)
    init_db(storage_dir)
    sent_marker = storage_dir / ".notify_sent"

    all_progress = get_progress_history(storage_dir)
    today_date = get_logical_date()

    # Avoid sending the same notification multiple times per day
    if sent_marker.exists():
        try:
            if sent_marker.read_text().strip() == today_date:
                console.print(
                    "[dim]Notification already sent for today (skipped).[/dim]\n"
                )
                return True
        except OSError:
            pass
    today_progress = get_daily_summary(today_date, storage_dir)

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
        try:
            sent_marker.write_text(today_date)
        except OSError:
            pass
    else:
        console.print("[red]Telegram send failed (response not ok).[/red]\n")

    return sent
