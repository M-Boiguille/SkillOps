"""Database optimization helpers for Phase 5."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, List, Optional

from src.lms.database import get_connection, init_db
from src.lms.performance_profiling import explain_query_plan


TRACKING_INDEXES = {
    "idx_tracking_summary_date": (
        "CREATE INDEX IF NOT EXISTS idx_tracking_summary_date "
        "ON tracking_summary(date)"
    ),
    "idx_tracking_summary_date_activity": (
        "CREATE INDEX IF NOT EXISTS idx_tracking_summary_date_activity "
        "ON tracking_summary(date, activity_level)"
    ),
    "idx_tracking_summary_date_commits": (
        "CREATE INDEX IF NOT EXISTS idx_tracking_summary_date_commits "
        "ON tracking_summary(date, git_commits)"
    ),
}

CODE_SESSION_INDEXES = {
    "idx_code_sessions_date": (
        "CREATE INDEX IF NOT EXISTS idx_code_sessions_date " "ON code_sessions(date)"
    ),
    "idx_code_sessions_commit_time": (
        "CREATE INDEX IF NOT EXISTS idx_code_sessions_commit_time "
        "ON code_sessions(commit_time)"
    ),
}


def ensure_tracking_indexes(storage_path: Optional[Path] = None) -> List[str]:
    """Ensure tracking_summary indexes exist and return created names."""
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    created: List[str] = []
    for name, ddl in TRACKING_INDEXES.items():
        cursor.execute(ddl)
        created.append(name)

    conn.commit()
    conn.close()
    return created


def ensure_code_session_indexes(storage_path: Optional[Path] = None) -> List[str]:
    """Ensure code_sessions indexes exist and return created names."""
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    created: List[str] = []
    for name, ddl in CODE_SESSION_INDEXES.items():
        cursor.execute(ddl)
        created.append(name)

    conn.commit()
    conn.close()
    return created


def analyze_query_plan(
    query: str, params: Optional[Iterable] = None, storage_path: Optional[Path] = None
) -> List[tuple]:
    """Return EXPLAIN QUERY PLAN rows for a query."""
    conn = get_connection(storage_path)
    try:
        return explain_query_plan(conn, query, params=params)
    finally:
        conn.close()


def vacuum_db(storage_path: Optional[Path] = None) -> None:
    """Run VACUUM on the database."""
    conn = get_connection(storage_path)
    try:
        conn.execute("VACUUM")
        conn.commit()
    finally:
        conn.close()


class ConnectionPool:
    """Simple SQLite connection pool for reuse."""

    def __init__(self, storage_path: Optional[Path] = None, max_size: int = 2):
        self.storage_path = storage_path
        self.max_size = max_size
        self._pool: List = []
        self._in_use = 0

    def acquire(self):
        if self._pool:
            return self._pool.pop()
        if self._in_use >= self.max_size:
            raise RuntimeError("Connection pool exhausted")
        self._in_use += 1
        return get_connection(self.storage_path)

    def release(self, conn) -> None:
        if conn:
            self._pool.append(conn)

    @contextmanager
    def connection(self):
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)
