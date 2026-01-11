"""Rich display components for SkillOps LMS.

This module provides reusable Rich display components for tables, panels,
progress bars, and formatted text used throughout the CLI.
"""

from datetime import datetime
from typing import Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich import box

console = Console()


def create_metrics_table(metrics: dict[str, Any]) -> Table:
    """Create a formatted table displaying daily metrics.

    Args:
        metrics: Dictionary containing metric data with keys:
            - total_time: Time in seconds
            - cards_created: Number of cards
            - streak: Consecutive days
            - steps_completed: Number of steps completed (out of 8)

    Returns:
        Rich Table object ready to print.
    """
    table = Table(
        title="📊 Daily Metrics",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="cyan",
    )

    table.add_column("Metric", style="bold", width=25)
    table.add_column("Value", justify="right", width=20)
    table.add_column("Status", justify="center", width=10)

    # Steps completed
    steps_completed = metrics.get("steps_completed", 0)
    steps_status = (
        "✅" if steps_completed >= 7 else "⚠️" if steps_completed >= 4 else "❌"
    )
    table.add_row(
        "Steps Completed",
        f"{steps_completed}/8",
        steps_status,
    )

    # Time coded
    total_seconds = metrics.get("total_time", 0)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    time_str = f"{hours}h {minutes:02d}min"
    time_status = (
        "✅" if total_seconds >= 7200 else "⚠️" if total_seconds >= 3600 else "❌"
    )
    table.add_row(
        "⏱️  Time Coded",
        time_str,
        time_status,
    )

    # Cards created
    cards = metrics.get("cards_created", 0)
    cards_status = "✅" if cards >= 10 else "⚠️" if cards >= 5 else "❌"
    table.add_row(
        "📝 Cards Created",
        str(cards),
        cards_status,
    )

    # Streak
    streak = metrics.get("streak", 0)
    streak_emoji = "🔥" if streak >= 7 else "📅"
    table.add_row(
        f"{streak_emoji} Streak",
        f"{streak} days",
        "",
    )

    return table


def create_step_summary_table(steps_data: list[dict[str, Any]]) -> Table:
    """Create a table showing the status of all 8 steps.

    Args:
        steps_data: List of dictionaries with keys:
            - number: Step number (1-8)
            - name: Step name
            - emoji: Step emoji
            - completed: Boolean indicating completion
            - time_spent: Optional time in seconds

    Returns:
        Rich Table object ready to print.
    """
    table = Table(
        title="📋 Steps Overview",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Step", style="bold", width=20)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Time", justify="right", width=15)

    for step in steps_data:
        status = "●" if step.get("completed", False) else "○"
        style = "green" if step.get("completed", False) else "dim"

        time_spent = step.get("time_spent", 0)
        if time_spent > 0:
            minutes = time_spent // 60
            time_str = f"{minutes}min"
        else:
            time_str = "-"

        table.add_row(
            f"{step['emoji']} {step['name']}",
            status,
            time_str,
            style=style,
        )

    return table


def display_success_message(message: str, title: str = "Success") -> None:
    """Display a success message in a green panel.

    Args:
        message: The success message to display.
        title: Optional title for the panel (default: "Success").
    """
    panel = Panel(
        f"[green]{message}[/green]",
        title=f"✅ {title}",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def display_warning_message(message: str, title: str = "Warning") -> None:
    """Display a warning message in a yellow panel.

    Args:
        message: The warning message to display.
        title: Optional title for the panel (default: "Warning").
    """
    panel = Panel(
        f"[yellow]{message}[/yellow]",
        title=f"⚠️  {title}",
        border_style="yellow",
        padding=(1, 2),
    )
    console.print(panel)


def display_error_message(message: str, title: str = "Error") -> None:
    """Display an error message in a red panel.

    Args:
        message: The error message to display.
        title: Optional title for the panel (default: "Error").
    """
    panel = Panel(
        f"[red]{message}[/red]",
        title=f"❌ {title}",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


def display_info_panel(title: str, content: str, border_color: str = "blue") -> None:
    """Display an informational panel with custom styling.

    Args:
        title: Title for the panel.
        content: Content to display inside the panel.
        border_color: Color for the border (default: "blue").
    """
    panel = Panel(
        content,
        title=f"ℹ️  {title}",
        border_style=border_color,
        padding=(1, 2),
    )
    console.print(panel)


def create_progress_bar(description: str = "Processing") -> Progress:
    """Create a Rich progress bar with standard formatting.

    Args:
        description: Description text for the progress bar.

    Returns:
        Configured Progress object.
    """
    return Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    )


def format_time_duration(seconds: int) -> str:
    """Format seconds into a human-readable duration string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted string like "2h 30min" or "45min" or "0h 00min".
    """
    if seconds < 0:
        seconds = 0

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes:02d}min"
    else:
        return f"{minutes}min"


def format_date(date: datetime) -> str:
    """Format a datetime object for display.

    Args:
        date: Datetime object to format.

    Returns:
        Formatted date string like "11 janvier 2026".
    """
    # French month names
    months_fr = [
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    ]

    day = date.day
    month = months_fr[date.month - 1]
    year = date.year

    return f"{day} {month} {year}"


def display_section_header(title: str, emoji: str = "📌") -> None:
    """Display a section header with emoji.

    Args:
        title: The header title.
        emoji: Optional emoji to prepend (default: "📌").
    """
    console.print()
    console.print(f"[bold cyan]{emoji} {title}[/bold cyan]")
    console.print("[cyan]" + "─" * (len(title) + 3) + "[/cyan]")
    console.print()
