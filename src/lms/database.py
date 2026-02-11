"""Database module for SkillOps - SQLite connection and schema management."""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from src.lms.paths import get_storage_path

DB_NAME = "skillops.db"
SCHEMA_VERSION = 2


def get_db_path(storage_path: Optional[Path] = None) -> Path:
    """Get the database file path."""
    resolved_path = Path(storage_path) if storage_path else get_storage_path()
    resolved_path.mkdir(parents=True, exist_ok=True)
    return resolved_path / DB_NAME


def get_connection(storage_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    return sqlite3.connect(get_db_path(storage_path))


def init_db(storage_path: Optional[Path] = None):
    """Initialize the database schema."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    # Sessions (Daily)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE, -- Logical date YYYY-MM-DD
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    )

    # Step Completions
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS step_completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        step_number INTEGER NOT NULL,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        UNIQUE(session_id, step_number)
    );
    """
    )

    # Context (Key-Value store for session context)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS context (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    )

    # Formation Logs
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS formation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        goals TEXT, -- JSON
        recall TEXT,
        duration_minutes INTEGER,
        wakatime_minutes INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );
    """
    )

    # Reinforce Progress
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS reinforce_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id TEXT NOT NULL,
        title TEXT NOT NULL,
        duration_seconds INTEGER,
        completed BOOLEAN,
        quality INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        srs_data TEXT -- JSON
    );
    """
    )

    # Card Creations
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS card_creations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        count INTEGER,
        source TEXT, -- 'tutor', 'create', etc.
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );
    """
    )

    # Read Sessions
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS read_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        notes TEXT, -- JSON list of note paths
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );
    """
    )

    # Performance Metrics
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        step_id TEXT NOT NULL,
        duration_seconds REAL NOT NULL,
        success BOOLEAN NOT NULL,
        api_calls INTEGER DEFAULT 0,
        items_processed INTEGER DEFAULT 0,
        metadata TEXT -- JSON
    );
    """
    )

    # Chaos Events
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS chaos_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level INTEGER NOT NULL,
        mode TEXT NOT NULL,
        action TEXT NOT NULL,
        target TEXT NOT NULL,
        status TEXT NOT NULL,
        details TEXT -- JSON
    );
    """
    )

    # Incidents (On-Call)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        affected_system TEXT NOT NULL,
        symptoms TEXT NOT NULL,
        status TEXT NOT NULL,
        resolution TEXT,
        postmortem_id INTEGER,
        FOREIGN KEY (postmortem_id) REFERENCES postmortems(id)
    );
    """
    )

    # Post-Mortems
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS postmortems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        what_happened TEXT NOT NULL,
        when_detected TEXT NOT NULL,
        impact TEXT NOT NULL,
        root_cause TEXT NOT NULL,
        resolution TEXT NOT NULL,
        prevention TEXT NOT NULL,
        action_items TEXT NOT NULL,
        FOREIGN KEY (incident_id) REFERENCES incidents(id)
    );
    """
    )

    _apply_migrations(conn)
    conn.commit()
    conn.close()


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Apply schema migrations to reach the latest version."""
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"
    )
    cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
    row = cursor.fetchone()
    current_version = row[0] if row else 0

    if current_version < 1:
        cursor.execute("INSERT INTO schema_version (version) VALUES (1)")
        current_version = 1

    if current_version < 2:
        _migration_add_wakatime_minutes(cursor)
        cursor.execute("INSERT INTO schema_version (version) VALUES (2)")


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def _migration_add_wakatime_minutes(cursor: sqlite3.Cursor) -> None:
    """Add wakatime_minutes column to formation_logs if missing."""
    if not _column_exists(cursor, "formation_logs", "wakatime_minutes"):
        cursor.execute(
            "ALTER TABLE formation_logs ADD COLUMN wakatime_minutes INTEGER DEFAULT 0"
        )


def get_logical_date() -> str:
    """Get the logical date (day starts at 4 AM)."""
    now = datetime.now()
    day_start_hour = int(os.getenv("SKILLOPS_DAY_START_HOUR", "4"))
    if now.hour < day_start_hour:
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    return now.strftime("%Y-%m-%d")


def get_current_session_id(storage_path: Optional[Path] = None) -> int:
    """Get or create the session ID for the current logical date."""
    date = get_logical_date()
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sessions WHERE date = ?", (date,))
    row = cursor.fetchone()

    if row:
        session_id = int(row[0])
    else:
        cursor.execute("INSERT INTO sessions (date) VALUES (?)", (date,))
        session_id = cursor.lastrowid
        conn.commit()

    conn.close()
    if session_id is None:
        raise RuntimeError("Failed to create session id")
    return int(session_id)
