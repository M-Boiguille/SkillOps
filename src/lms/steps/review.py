"""Review step - Display yesterday's metrics and current streak.

This step shows the user a summary of their performance from the previous day,
including completed steps, time coded, cards created, and current streak.
"""

from pathlib import Path
from datetime import datetime, timedelta
from src.lms.persistence import MetricsManager, ProgressManager
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


def format_step_data_for_display(progress_data: dict) -> list[dict]:
    """Convert progress data to format expected by display components.

    Args:
        progress_data: Progress data for a specific date.

    Returns:
        List of step dictionaries for create_step_summary_table().
    """
    step_names = [
        "Review",
        "Formation",
        "Anki",
        "Create",
        "Read",
        "Reinforce",
        "Share",
        "Reflection",
    ]
    step_emojis = ["📊", "⏱️", "🗂️", "📝", "📖", "💪", "🌐", "🌅"]

    steps = progress_data.get("steps", {})

    step_data = []
    for i in range(1, 9):
        step_key = f"step{i}"
        step_info = steps.get(step_key, {})

        step_data.append(
            {
                "number": i,
                "name": step_names[i - 1],
                "emoji": step_emojis[i - 1],
                "completed": step_info.get("completed", False),
                "time_spent": step_info.get("time_spent", 0),
            }
        )

    return step_data


def calculate_metrics_from_progress(
    progress_data: dict, all_progress_data: dict
) -> dict:
    """Calculate metrics for display from progress data.

    Args:
        progress_data: Progress data for a specific date.
        all_progress_data: All progress data (dict with dates as keys).

    Returns:
        Dictionary with keys: steps_completed, total_time, cards_created, streak.
    """
    # Count completed steps
    steps = progress_data.get("steps", {})
    steps_completed = sum(
        1 for step_data in steps.values() if step_data.get("completed", False)
    )

    # Calculate total time
    total_time = sum(step_data.get("time_spent", 0) for step_data in steps.values())

    # Get cards created
    cards_created = progress_data.get("cards_created", 0)

    # Calculate streak using MetricsManager
    # Convert dict format to list format expected by calculate_streak
    progress_list = [
        {"date": date_str, **data} for date_str, data in all_progress_data.items()
    ]

    temp_metrics_path = Path("storage/metrics_temp.json")
    metrics_manager = MetricsManager(temp_metrics_path)
    streak = metrics_manager.calculate_streak(progress_list)

    return {
        "steps_completed": steps_completed,
        "total_time": total_time,
        "cards_created": cards_created,
        "streak": streak,
    }


def review_step(storage_path: Path = Path("storage")) -> None:
    """Execute the Review step - display yesterday's metrics.

    Args:
        storage_path: Path to the storage directory (default: "storage").
    """
    display_section_header("Review Yesterday's Progress", emoji="📊")

    # Initialize managers
    progress_file = storage_path / "progress.json"
    progress_manager = ProgressManager(progress_file)

    # Load progress data
    all_progress = progress_manager.load_progress()

    # Get yesterday's date
    yesterday_date = get_yesterday_date()
    yesterday_datetime = datetime.strptime(yesterday_date, "%Y-%m-%d")

    # Get yesterday's progress
    yesterday_progress = progress_manager.get_progress_by_date(yesterday_date)

    if not yesterday_progress or not yesterday_progress.get("steps"):
        console.print(
            f"[yellow]No data found for {format_date(yesterday_datetime)}[/yellow]"
        )
        console.print("[dim]Complete some steps today to see them tomorrow![/dim]\n")
        return

    # Calculate metrics
    metrics = calculate_metrics_from_progress(yesterday_progress, all_progress)

    # Display date header
    console.print(f"[bold cyan]Date:[/bold cyan] {format_date(yesterday_datetime)}\n")

    # Display metrics table
    metrics_table = create_metrics_table(metrics)
    console.print(metrics_table)
    console.print()

    # Display steps summary
    step_data = format_step_data_for_display(yesterday_progress)
    steps_table = create_step_summary_table(step_data)
    console.print(steps_table)
    console.print()

    # Display motivational message based on performance
    if metrics["steps_completed"] >= 7:
        console.print(
            "[bold green]🎉 Excellent work! You completed almost all steps![/bold green]\n"
        )
    elif metrics["steps_completed"] >= 5:
        console.print("[bold yellow]👍 Good progress! Keep it up![/bold yellow]\n")
    else:
        console.print(
            "[yellow]There's room for improvement. Try to complete more steps today![/yellow]\n"
        )
