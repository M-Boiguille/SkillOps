"""TUI Dashboard for SkillOps (Phase 4).

Provides an interactive Rich terminal UI for visualizing metrics and analytics.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from src.lms.database import get_connection, get_logical_date

console = Console()


def get_historical_tracking(
    days: int = 7, storage_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Get tracking data for the past N days.

    Args:
        days: Number of days to retrieve
        storage_path: Optional custom storage directory

    Returns:
        List of daily tracking summaries
    """
    try:
        conn = get_connection(storage_path)
        cursor = conn.cursor()

        today = datetime.strptime(get_logical_date(), "%Y-%m-%d").date()
        start_date = today - timedelta(days=days - 1)

        cursor.execute(
            """
        SELECT date, wakatime_seconds, git_commits, git_files_changed,
               git_lines_added, git_lines_deleted, activity_level
        FROM tracking_summary
        WHERE date >= ?
        ORDER BY date DESC
        """,
            (start_date.strftime("%Y-%m-%d"),),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "date": r[0],
                "wakatime_seconds": r[1],
                "git_commits": r[2],
                "git_files_changed": r[3],
                "git_lines_added": r[4],
                "git_lines_deleted": r[5],
                "activity_level": r[6],
            }
            for r in rows
        ]

    except Exception:
        return []


def create_weekly_summary_table(
    tracking_data: List[Dict[str, Any]],
) -> Table:
    """Create a table showing weekly tracking summary.

    Args:
        tracking_data: List of daily tracking summaries

    Returns:
        Rich Table with weekly stats
    """
    table = Table(title="Last 7 Days Activity", show_header=True)
    table.add_column("Date", style="cyan")
    table.add_column("Time", style="green")
    table.add_column("Commits", style="magenta")
    table.add_column("Changes", style="yellow")
    table.add_column("Level", style="blue")

    for day_data in tracking_data[:7]:  # Last 7 days
        date_str = day_data["date"]
        wakatime_s = day_data["wakatime_seconds"]
        hours = wakatime_s // 3600
        minutes = (wakatime_s % 3600) // 60
        time_str = f"{hours}h {minutes}m" if wakatime_s > 0 else "—"

        commits = day_data["git_commits"]
        changes = day_data["git_lines_added"] + day_data["git_lines_deleted"]

        activity = day_data["activity_level"] or "—"

        table.add_row(
            date_str,
            time_str,
            str(commits),
            str(changes),
            activity.capitalize(),
        )

    return table


def create_stats_panel(tracking_data: List[Dict[str, Any]]) -> Panel:
    """Create a panel with aggregated statistics.

    Args:
        tracking_data: List of daily tracking summaries

    Returns:
        Rich Panel with stats
    """
    if not tracking_data:
        return Panel("No data available", title="Statistics")

    # Calculate 7-day stats
    total_time_seconds = sum(d["wakatime_seconds"] for d in tracking_data[:7])
    total_commits = sum(d["git_commits"] for d in tracking_data[:7])
    total_changes = sum(
        d["git_lines_added"] + d["git_lines_deleted"] for d in tracking_data[:7]
    )
    avg_daily_time = total_time_seconds / 7 if total_time_seconds > 0 else 0

    # Format times
    total_hours = total_time_seconds // 3600
    total_mins = (total_time_seconds % 3600) // 60
    avg_hours = int(avg_daily_time) // 3600
    avg_mins = (int(avg_daily_time) % 3600) // 60

    stats_text = Text()
    stats_text.append("📊 Weekly Summary (Last 7 Days)\n\n", style="bold cyan")
    stats_text.append(f"💻 Total Coding Time: {total_hours}h {total_mins}m\n")
    stats_text.append(f"📦 Total Commits: {total_commits}\n")
    stats_text.append(f"📝 Total Changes: {total_changes} lines\n")
    stats_text.append(f"⏱️  Avg Daily Time: {avg_hours}h {avg_mins}m\n")

    return Panel(stats_text, title="Statistics", expand=False)


def create_trends_table(tracking_data: List[Dict[str, Any]]) -> Table:
    """Create a table showing activity trends.

    Args:
        tracking_data: List of daily tracking summaries

    Returns:
        Rich Table with trend analysis
    """
    table = Table(title="Activity Trends", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Trend", style="green")
    table.add_column("Value", style="yellow")

    if len(tracking_data) < 2:
        table.add_row("Commits", "—", "Not enough data")
        return table

    # Compare first half vs second half
    mid = len(tracking_data) // 2
    recent = tracking_data[:mid]
    older = tracking_data[mid:]

    recent_commits = sum(d["git_commits"] for d in recent)
    older_commits = sum(d["git_commits"] for d in older)

    if older_commits > 0:
        commit_change = ((recent_commits - older_commits) / older_commits) * 100
        trend_emoji = "📈" if commit_change > 0 else "📉"
        table.add_row(
            "Commits",
            f"{trend_emoji} {commit_change:+.0f}%",
            str(recent_commits),
        )
    else:
        table.add_row("Commits", "—", str(recent_commits))

    recent_time = sum(d["wakatime_seconds"] for d in recent)
    older_time = sum(d["wakatime_seconds"] for d in older)

    if older_time > 0:
        time_change = ((recent_time - older_time) / older_time) * 100
        trend_emoji = "📈" if time_change > 0 else "📉"
        table.add_row(
            "Coding Time",
            f"{trend_emoji} {time_change:+.0f}%",
            f"{recent_time // 3600}h",
        )
    else:
        table.add_row("Coding Time", "—", f"{recent_time // 3600}h")

    return table


def display_dashboard(storage_path: Optional[Path] = None) -> None:
    """Display the main TUI dashboard.

    Args:
        storage_path: Optional custom storage directory
    """
    console.print("\n[bold cyan]SkillOps Dashboard - Phase 4[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Loading metrics...", total=None)

        # Load data
        tracking_data = get_historical_tracking(days=7, storage_path=storage_path)

    if not tracking_data:
        console.print(
            "[yellow]No tracking data yet. "
            "Run 'skillops code' to start tracking.[/yellow]\n"
        )
        return

    # Create layout
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=2),
    )

    # Header
    layout["header"].update(
        Panel("[bold cyan]SkillOps Learning Dashboard[/bold cyan]", expand=False)
    )

    # Body with two columns
    layout["body"].split_column(
        Layout(name="left"),
        Layout(name="right"),
    )

    layout["left"].update(Layout(create_weekly_summary_table(tracking_data)))
    layout["left"].split_row(
        Layout(create_stats_panel(tracking_data)),
        Layout(create_trends_table(tracking_data)),
    )

    # Footer
    footer_text = Text(
        f"Last updated: {get_logical_date()} | Run: skillops code",
        style="dim",
    )
    layout["footer"].update(Panel(footer_text, expand=False))

    # Display
    console.print(layout)
    console.print()


def get_learning_recommendations(
    storage_path: Optional[Path] = None,
) -> List[str]:
    """Generate adaptive learning recommendations based on patterns.

    Args:
        storage_path: Optional custom storage directory

    Returns:
        List of recommendation strings
    """
    try:
        tracking_data = get_historical_tracking(days=7, storage_path=storage_path)

        if not tracking_data:
            return ["✨ Start tracking with 'skillops code' to get recommendations"]

        recommendations = []

        # Analyze activity patterns
        total_commits = sum(d["git_commits"] for d in tracking_data)
        total_time = sum(d["wakatime_seconds"] for d in tracking_data)
        active_days = sum(1 for d in tracking_data if d["git_commits"] > 0)

        # Consistency check
        if active_days < 4:
            recommendations.append(
                "🎯 Try to maintain consistency: aim for 5+ active days per week"
            )

        # Intensity check
        if total_time < 21600:  # < 6 hours per week
            recommendations.append(
                "⚡ Increase coding time: target at least 1h per day"
            )

        # Productivity check
        if total_commits > 0 and total_time > 0:
            commits_per_hour = total_commits / (total_time / 3600)
            if commits_per_hour < 0.5:
                recommendations.append(
                    "📦 More frequent commits: smaller, logical commits improve tracking"
                )

        # Momentum check
        if tracking_data[0]["git_commits"] == 0:
            recommendations.append("🚀 Code today to maintain your streak!")

        if not recommendations:
            recommendations.append("✨ Great consistency! Keep up the momentum!")

        return recommendations

    except Exception:
        return []


def display_recommendations(storage_path: Optional[Path] = None) -> None:
    """Display personalized learning recommendations.

    Args:
        storage_path: Optional custom storage directory
    """
    recommendations = get_learning_recommendations(storage_path=storage_path)

    console.print("\n[bold yellow]💡 Recommendations[/bold yellow]\n")

    for rec in recommendations:
        console.print(f"  {rec}")

    console.print()
