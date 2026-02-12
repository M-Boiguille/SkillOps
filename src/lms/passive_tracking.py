"""Passive code tracking integration (Phase 3).

Combines WakaTime API data + git commit history to provide comprehensive
coding session metrics without requiring explicit user interaction.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from src.lms.database import get_connection, init_db
from src.lms.database import get_logical_date
from src.lms.api_clients.wakatime_client import WakaTimeClient, WakaTimeError
from src.lms.git_hooks import calculate_session_metrics as calculate_git_metrics


def merge_session_data(
    wakatime_data: Optional[Dict[str, Any]] = None,
    git_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Merge WakaTime and git data into a comprehensive session view.

    Args:
        wakatime_data: Data from WakaTime API
        git_data: Data from git commits

    Returns:
        Merged session metrics
    """
    wakatime_data = wakatime_data or {}
    git_data = git_data or {}

    return {
        "date": get_logical_date(),
        "wakatime": {
            "total_seconds": wakatime_data.get("total_seconds", 0),
            "languages": wakatime_data.get("languages", []),
            "projects": wakatime_data.get("projects", []),
            "editors": wakatime_data.get("editors", []),
        },
        "git": {
            "commits": git_data.get("commits_count", 0),
            "files_changed": git_data.get("files_changed", 0),
            "lines_added": git_data.get("lines_added", 0),
            "lines_deleted": git_data.get("lines_deleted", 0),
        },
        "summary": {
            "total_coding_time_seconds": wakatime_data.get("total_seconds", 0),
            "total_changes": git_data.get("total_changes", 0),
            "activity_level": _estimate_activity_level(
                wakatime_data.get("total_seconds", 0),
                git_data.get("commits_count", 0),
            ),
        },
    }


def _estimate_activity_level(total_seconds: int, commits: int) -> str:
    """Estimate activity level (inactive, low, moderate, high).

    Args:
        total_seconds: Total coding time in seconds
        commits: Number of commits

    Returns:
        Activity level string
    """
    if total_seconds == 0 and commits == 0:
        return "inactive"
    elif total_seconds < 1800 and commits < 3:  # < 30 min or < 3 commits
        return "low"
    elif total_seconds < 3600 and commits < 10:  # < 1 hour or < 10 commits
        return "moderate"
    else:
        return "high"


def collect_daily_tracking_data(
    storage_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Collect all tracking data for today from all sources.

    This is the main entry point for Phase 3 passive tracking.

    Args:
        storage_path: Optional custom storage directory

    Returns:
        Dictionary with comprehensive session data
    """
    init_db(storage_path=storage_path)

    wakatime_data = {}
    git_data = {}

    # Try to fetch WakaTime data
    try:
        client = WakaTimeClient()
        stats = client.get_today_stats()

        if stats:
            wakatime_data = {
                "total_seconds": stats.get("total_seconds", 0),
                "languages": [
                    {
                        "name": lang.get("name"),
                        "percent": lang.get("percent"),
                        "total_seconds": lang.get("total_seconds"),
                    }
                    for lang in stats.get("languages", [])[:5]  # Top 5 languages
                ],
                "projects": [
                    {
                        "name": p.get("name"),
                        "percent": p.get("percent"),
                        "total_seconds": p.get("total_seconds"),
                    }
                    for p in stats.get("projects", [])[:3]  # Top 3 projects
                ],
                "editors": [
                    {
                        "name": e.get("name"),
                        "percent": e.get("percent"),
                    }
                    for e in stats.get("editors", [])[:2]  # Top 2 editors
                ],
            }
    except WakaTimeError:
        # WakaTime API not available - continue with git data
        pass

    # Collect git data
    try:
        git_data = calculate_git_metrics(storage_path=storage_path)
    except Exception:
        pass

    # Store tracking data in SQLite
    _store_tracking_data(wakatime_data, git_data, storage_path=storage_path)

    return merge_session_data(wakatime_data, git_data)


def _store_tracking_data(
    wakatime_data: Dict[str, Any],
    git_data: Dict[str, Any],
    storage_path: Optional[Path] = None,
) -> None:
    """Store collected tracking data to SQLite.

    Args:
        wakatime_data: WakaTime metrics
        git_data: Git metrics
        storage_path: Optional custom storage directory
    """
    try:
        conn = get_connection(storage_path=storage_path)
        cursor = conn.cursor()

        # Ensure tracking_summary table exists
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tracking_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            wakatime_seconds INTEGER DEFAULT 0,
            git_commits INTEGER DEFAULT 0,
            git_files_changed INTEGER DEFAULT 0,
            git_lines_added INTEGER DEFAULT 0,
            git_lines_deleted INTEGER DEFAULT 0,
            activity_level TEXT,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
        )

        today = get_logical_date()

        cursor.execute(
            """
        INSERT OR REPLACE INTO tracking_summary
        (date, wakatime_seconds, git_commits, git_files_changed, git_lines_added,
         git_lines_deleted, activity_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                today,
                wakatime_data.get("total_seconds", 0),
                git_data.get("commits_count", 0),
                git_data.get("files_changed", 0),
                git_data.get("lines_added", 0),
                git_data.get("lines_deleted", 0),
                _estimate_activity_level(
                    wakatime_data.get("total_seconds", 0),
                    git_data.get("commits_count", 0),
                ),
            ),
        )

        conn.commit()
        conn.close()

    except Exception:
        pass


def get_tracking_summary(
    date_str: Optional[str] = None,
    storage_path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """Get tracking summary for a specific date.

    Args:
        date_str: Date in YYYY-MM-DD format (default: today)
        storage_path: Optional custom storage directory

    Returns:
        Dictionary with tracking data, or None if not found
    """
    try:
        date_str = date_str or get_logical_date()
        conn = get_connection(storage_path=storage_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT wakatime_seconds, git_commits, git_files_changed,
               git_lines_added, git_lines_deleted, activity_level
        FROM tracking_summary
        WHERE date = ?
        """,
            (date_str,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "date": date_str,
            "wakatime_seconds": row[0],
            "git_commits": row[1],
            "git_files_changed": row[2],
            "git_lines_added": row[3],
            "git_lines_deleted": row[4],
            "activity_level": row[5],
        }

    except Exception:
        return None
