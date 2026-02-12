"""Git hooks integration for passive code tracking.

Automatically records commit metadata to track coding sessions.
Integrates with WakaTime for time-tracking intelligence.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from src.lms.database import get_connection, init_db
from src.lms.database import get_logical_date


def install_post_commit_hook(repo_path: Optional[Path] = None) -> bool:
    """Install a post-commit hook in the repository.

    This hook automatically records commit metadata to SQLite.

    Args:
        repo_path: Git repository path (default: current dir)

    Returns:
        True if hook installed successfully, False otherwise
    """
    try:
        repo_path = Path(repo_path or ".")
        git_dir = repo_path / ".git"

        if not git_dir.exists():
            return False

        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir(exist_ok=True, parents=True)

        hook_path = hooks_dir / "post-commit"

        # Hook script that records commit data
        hook_script = """#!/bin/bash
# SkillOps auto-tracking hook
# Records commit metadata for passive coding session tracking

COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_TIME=$(git log -1 --format=%aI)
COMMIT_MSG=$(git log -1 --format=%B)
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD | wc -l)
LINES_ADDED=$(git diff-tree --no-commit-id --numstat -r HEAD | awk '{sum+=$1} END {print sum}')
LINES_DELETED=$(git diff-tree --no-commit-id --numstat -r HEAD | awk '{sum+=$2} END {print sum}')

# Call Python to record this to SQLite
python3 -c "
import sys
sys.path.insert(0, '.')
from src.lms.git_hooks import record_commit_to_db
record_commit_to_db(
    commit_hash='$COMMIT_HASH',
    commit_time='$COMMIT_TIME',
    commit_msg='$COMMIT_MSG',
    files_changed=$FILES_CHANGED,
    lines_added=${LINES_ADDED:-0},
    lines_deleted=${LINES_DELETED:-0}
)
" 2>/dev/null || true
"""

        hook_path.write_text(hook_script)
        hook_path.chmod(0o755)

        return True

    except Exception:
        return False


def record_commit_to_db(
    commit_hash: str,
    commit_time: str,
    commit_msg: str,
    files_changed: int,
    lines_added: int,
    lines_deleted: int,
    storage_path: Optional[Path] = None,
) -> bool:
    """Record a commit to the code_sessions table in SQLite.

    Args:
        commit_hash: Git commit SHA
        commit_time: ISO timestamp of commit
        commit_msg: Commit message
        files_changed: Number of files modified
        lines_added: Lines added
        lines_deleted: Lines deleted
        storage_path: Optional custom storage directory

    Returns:
        True if recorded successfully, False otherwise
    """
    try:
        init_db(storage_path=storage_path)
        conn = get_connection(storage_path=storage_path)
        cursor = conn.cursor()

        # Ensure code_sessions table exists
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS code_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            commit_hash TEXT UNIQUE NOT NULL,
            commit_time TEXT NOT NULL,
            commit_msg TEXT,
            files_changed INTEGER,
            lines_added INTEGER,
            lines_deleted INTEGER,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            date TEXT NOT NULL
        );
        """
        )

        # Extract date from commit_time (YYYY-MM-DD)
        try:
            commit_datetime = datetime.fromisoformat(commit_time.replace("Z", "+00:00"))
            date_str = commit_datetime.strftime("%Y-%m-%d")
        except Exception:
            date_str = get_logical_date()

        cursor.execute(
            """
        INSERT OR IGNORE INTO code_sessions
        (commit_hash, commit_time, commit_msg, files_changed, lines_added, lines_deleted, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                commit_hash,
                commit_time,
                commit_msg,
                files_changed,
                lines_added,
                lines_deleted,
                date_str,
            ),
        )

        conn.commit()
        conn.close()

        return True

    except Exception:
        return False


def get_today_commits(storage_path: Optional[Path] = None) -> list[Dict[str, Any]]:
    """Get all commits recorded today.

    Args:
        storage_path: Optional custom storage directory

    Returns:
        List of commit records for today
    """
    try:
        conn = get_connection(storage_path=storage_path)
        cursor = conn.cursor()

        today = get_logical_date()

        cursor.execute(
            """
        SELECT commit_hash, commit_time, commit_msg, files_changed, lines_added, lines_deleted
        FROM code_sessions
        WHERE date = ?
        ORDER BY commit_time DESC
        """,
            (today,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "hash": r[0],
                "time": r[1],
                "message": r[2],
                "files_changed": r[3],
                "lines_added": r[4],
                "lines_deleted": r[5],
            }
            for r in rows
        ]

    except Exception:
        return []


def calculate_session_metrics(
    storage_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Calculate coding session metrics from commits.

    Args:
        storage_path: Optional custom storage directory

    Returns:
        Dictionary with session metrics
    """
    commits = get_today_commits(storage_path=storage_path)

    if not commits:
        return {
            "commits_count": 0,
            "files_changed": 0,
            "lines_added": 0,
            "lines_deleted": 0,
            "total_changes": 0,
        }

    return {
        "commits_count": len(commits),
        "files_changed": sum(c["files_changed"] for c in commits),
        "lines_added": sum(c["lines_added"] for c in commits),
        "lines_deleted": sum(c["lines_deleted"] for c in commits),
        "total_changes": sum(c["lines_added"] + c["lines_deleted"] for c in commits),
    }
