"""Review step - Display yesterday's metrics and current streak.

This step shows the user a summary of their performance from the previous day,
including completed steps, time coded, cards created, and current streak.
"""

from pathlib import Path
from datetime import datetime, timedelta
from src.lms.persistence import get_daily_summary, calculate_streak
from src.lms.display import (
    create_metrics_table,
    create_step_summary_table,
    display_section_header,
    format_date,
    console,
)


def get_yesterday_date() -> str:
    """Get yesterday's date in YYYY-MM-DD format.

    Returns:
        Yesterday's date as string.
    """
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def format_step_data_for_display(summary_data: dict) -> list[dict]:
    """Convert progress data to format expected by display components.

    Args:
        summary_data: Summary data from DB.

    Returns:
        List of step dictionaries for create_step_summary_table().
    """
    step_names = [
        "Daily Stand-up",
        "Read",
        "Tutor",
        "Reinforce",
        "Create",
        "Flashcards",
        "Mission Control",
        "Pull Request",
        "Reflection",
    ]
    step_emojis = ["📊", "📖", "🧠", "💪", "📝", "🗂️", "🚀", "🌐", "🌅"]

    completed_steps = summary_data.get("steps_list", [])
    step_durations = summary_data.get("step_durations", {})
    step_data = []

    for i in range(1, 10):
        step_data.append(
            {
                "number": i,
                "name": step_names[i - 1],
                "emoji": step_emojis[i - 1],
                "completed": i in completed_steps,
                "time_spent": int(step_durations.get(i, 0)),
            }
        )

    return step_data


def calculate_metrics_from_progress(progress: dict, history: list[dict]) -> dict:
    """Calculate metrics from SQLite summary data."""
    steps_completed = int(progress.get("steps_completed", 0))
    total_minutes = int(progress.get("total_time_minutes", 0))
    cards_created = int(progress.get("cards_created", 0))
    return {
        "steps_completed": steps_completed,
        "total_time": total_minutes * 60,
        "cards_created": cards_created,
        "streak": calculate_streak(),
    }


def daily_standup_step() -> bool:
    """Legacy alias for the daily stand-up workflow."""
    return review_step()


def review_step(storage_path: Path = Path("storage")) -> bool:
    """Execute the Review step - display yesterday's metrics.

    Args:
        storage_path: Path to the storage directory (default: "storage").
    """
    display_section_header("Daily Stand-up", emoji="📊")

    # Get yesterday's date
    yesterday_date = get_yesterday_date()
    yesterday_datetime = datetime.strptime(yesterday_date, "%Y-%m-%d")

    # Get yesterday's progress
    summary = get_daily_summary(yesterday_date, storage_path)

    if not summary:
        console.print(
            f"[yellow]No data found for {format_date(yesterday_datetime)}[/yellow]"
        )
        console.print("[dim]Complete some steps today to see them tomorrow![/dim]\n")
        return True

    # Prepare metrics
    metrics = {
        "steps_completed": summary.get("steps_completed", 0),
        "total_time": summary.get("total_time_minutes", 0)
        * 60,  # Convert back to seconds for display util if needed
        "cards_created": summary.get("cards_created", 0),
        "streak": calculate_streak(storage_path),
    }

    # Display date header
    console.print(f"[bold cyan]Date:[/bold cyan] {format_date(yesterday_datetime)}\n")

    # Display metrics table
    metrics_table = create_metrics_table(metrics)
    console.print(metrics_table)
    console.print()

    # Display steps summary
    step_data = format_step_data_for_display(summary)
    steps_table = create_step_summary_table(step_data)
    console.print(steps_table)
    console.print()

    # Encouragement
    if metrics["steps_completed"] >= 8:
        console.print(
            "[bold green]🎉 Excellent work! You completed almost all steps![/bold green]\n"
        )
    elif metrics["steps_completed"] >= 5:
        console.print("[bold yellow]👍 Good progress! Keep it up![/bold yellow]\n")
    else:
        console.print(
            "[yellow]There's room for improvement. Try to complete more steps today![/yellow]\n"
        )
    return True
