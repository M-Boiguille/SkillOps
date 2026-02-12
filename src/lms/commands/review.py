"""Review command: show streak and daily stats."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from src.lms.database import get_logical_date, init_db
from src.lms.display import create_metrics_table
from src.lms.persistence import calculate_streak, get_daily_summary

console = Console()


def run_review(storage_path: Optional[Path] = None) -> None:
    """Run the review command to display current stats."""
    init_db(storage_path=storage_path)

    date_str = get_logical_date()
    summary = get_daily_summary(date_str, storage_path=storage_path)
    streak = calculate_streak(storage_path=storage_path)

    if not summary:
        console.print(
            Panel(
                "Aucune session trouvée pour aujourd'hui.\n"
                "Lance `skillops train <topic>` ou `skillops code`.",
                border_style="yellow",
            )
        )
        summary = {
            "total_time_minutes": 0,
            "cards_created": 0,
            "steps_completed": 0,
        }

    metrics = {
        "total_time": (summary.get("total_time_minutes", 0) or 0) * 60,
        "cards_created": summary.get("cards_created", 0) or 0,
        "streak": streak,
        "steps_completed": summary.get("steps_completed", 0) or 0,
    }

    console.print(create_metrics_table(metrics))
