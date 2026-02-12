"""Code command: passive tracking with WakaTime + git hooks (Phase 3)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from src.lms.database import get_current_session_id, init_db
from src.lms.passive_tracking import collect_daily_tracking_data
from src.lms.git_hooks import install_post_commit_hook

console = Console()


def run_code(storage_path: Optional[Path] = None) -> None:
    """Run the code command with passive tracking (Phase 3).

    Collects and displays:
    - WakaTime coding statistics (if available)
    - Git commit history for today
    - Combined activity metrics
    """
    init_db(storage_path=storage_path)
    get_current_session_id(storage_path=storage_path)

    console.print("\n[bold cyan]Code - Passive Tracking (Phase 3)[/bold cyan]\n")

    # Try to install git hooks (silent fail if not in git repo)
    install_post_commit_hook()

    # Collect tracking data from WakaTime + git
    tracking_data = collect_daily_tracking_data(storage_path=storage_path)

    # Display results in a table
    table = Table(title="Today's Coding Activity", show_header=True)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    # WakaTime data
    wakatime = tracking_data.get("wakatime", {})
    wakatime_seconds = wakatime.get("total_seconds", 0)
    wakatime_hours = wakatime_seconds // 3600
    wakatime_minutes = (wakatime_seconds % 3600) // 60
    table.add_row("💻 WakaTime Coding", f"{wakatime_hours}h {wakatime_minutes}m")

    # Languages
    languages = wakatime.get("languages", [])
    if languages:
        lang_str = ", ".join(
            f"{lang['name']} ({lang['percent']:.0f}%)" for lang in languages[:3]
        )
        table.add_row("🔤 Languages", lang_str)

    # Git commits
    git_data = tracking_data.get("git", {})
    commits = git_data.get("commits", 0)
    table.add_row("📦 Commits", str(commits))

    if commits > 0:
        files = git_data.get("files_changed", 0)
        added = git_data.get("lines_added", 0)
        deleted = git_data.get("lines_deleted", 0)
        table.add_row("📝 Files Changed", str(files))
        table.add_row("➕ Lines Added", str(added))
        table.add_row("➖ Lines Deleted", str(deleted))

    # Activity level
    summary = tracking_data.get("summary", {})
    activity = summary.get("activity_level", "inactive")
    table.add_row("⚡ Activity Level", activity.capitalize())

    console.print(table)

    # Show next steps
    console.print("\n[dim]Phase 3 passive tracking active:[/dim]")
    console.print("[dim]  • Git hooks automatically record commits[/dim]")
    console.print("[dim]  • WakaTime API integration (if WAKATIME_API_KEY set)[/dim]")
    console.print("[dim]  • Run this command anytime to see daily metrics[/dim]\n")
