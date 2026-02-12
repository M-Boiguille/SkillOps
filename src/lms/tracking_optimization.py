"""Tracking pipeline optimizations for Phase 5."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

from src.lms.database import get_connection


def batch_insert_code_sessions(
    commits: Iterable[Dict[str, Any]], storage_path: Optional[Path] = None
) -> int:
    """Insert multiple commit records in a single transaction."""
    rows = []
    for commit in commits:
        required = {
            "commit_hash",
            "commit_time",
            "commit_msg",
            "files_changed",
            "lines_added",
            "lines_deleted",
        }
        if not required.issubset(commit.keys()):
            raise ValueError("Missing required commit fields")
        commit_time = str(commit["commit_time"])
        commit_date = commit_time.split("T")[0]
        rows.append(
            (
                commit["commit_hash"],
                commit_time,
                commit["commit_msg"],
                int(commit["files_changed"]),
                int(commit["lines_added"]),
                int(commit["lines_deleted"]),
                commit_date,
            )
        )

    if not rows:
        return 0

    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR IGNORE INTO code_sessions
        (commit_hash, commit_time, commit_msg, files_changed, lines_added, lines_deleted, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    conn.close()
    return len(rows)


def stream_tracking_summary(
    days: int = 7, storage_path: Optional[Path] = None
) -> Iterator[Dict[str, Any]]:
    """Stream tracking_summary rows as dictionaries."""
    conn = get_connection(storage_path)
    try:
        cursor = conn.cursor()
        today = datetime.now().date()
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
        for row in cursor.fetchall():
            yield {
                "date": row[0],
                "wakatime_seconds": row[1],
                "git_commits": row[2],
                "git_files_changed": row[3],
                "git_lines_added": row[4],
                "git_lines_deleted": row[5],
                "activity_level": row[6],
            }
    finally:
        conn.close()


def reduce_tracking_data(
    tracking_data: List[Dict[str, Any]], max_days: int
) -> List[Dict[str, Any]]:
    """Trim tracking data list to the most recent max_days entries."""
    return tracking_data[:max_days]


def chunked(iterable: Iterable[Any], size: int) -> Iterator[List[Any]]:
    """Yield chunks of a fixed size from an iterable."""
    chunk: List[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
