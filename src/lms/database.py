"""Database module for SkillOps - SQLite connection and schema management."""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from src.lms.paths import get_storage_path

DB_NAME = "skillops.db"
SCHEMA_VERSION = 7


def get_db_path(storage_path: Optional[Path] = None) -> Path:
    """Get the database file path."""
    resolved_path = Path(storage_path) if storage_path else get_storage_path()
    resolved_path.mkdir(parents=True, exist_ok=True)
    return resolved_path / DB_NAME


def get_connection(storage_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(get_db_path(storage_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


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

    # Quiz Cards (SQLite-native flashcards)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS quiz_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        difficulty INTEGER,
        last_reviewed TEXT,
        review_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
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

    # User Learning Profile
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS user_learning_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE,
        current_topics TEXT, -- JSON list
        recent_achievements TEXT,
        learning_difficulty TEXT
    );
    """
    )

    # Chaos History (adaptive templates)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS chaos_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        template_name TEXT,
        attempt_date TEXT,
        user_answer TEXT,
        ai_feedback TEXT,
        success BOOLEAN
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
        resolution_score INTEGER,
        next_review_date TEXT,
        hints_used INTEGER DEFAULT 0,
        parent_incident_id INTEGER,
        difficulty_level INTEGER DEFAULT 1,
        generated_by TEXT DEFAULT 'template',
        FOREIGN KEY (postmortem_id) REFERENCES postmortems(id),
        FOREIGN KEY (parent_incident_id) REFERENCES incidents(id)
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
    _cleanup_old_records(conn)
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

    if current_version < 3:
        _migration_add_incident_srs_columns(cursor)
        cursor.execute("INSERT INTO schema_version (version) VALUES (3)")

    if current_version < 4:
        _migration_add_indexes(cursor)
        cursor.execute("INSERT INTO schema_version (version) VALUES (4)")

    if current_version < 5:
        _migration_add_quiz_cards(cursor)
        cursor.execute("INSERT INTO schema_version (version) VALUES (5)")

    if current_version < 6:
        _migration_add_learning_profile(cursor)
        _migration_add_chaos_history(cursor)
        cursor.execute("INSERT INTO schema_version (version) VALUES (6)")

    if current_version < 7:
        _migration_add_passive_tracking_tables(cursor)
        cursor.execute("INSERT INTO schema_version (version) VALUES (7)")


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def _index_exists(cursor: sqlite3.Cursor, index_name: str) -> bool:
    cursor.execute("PRAGMA index_list(incidents)")
    if any(row[1] == index_name for row in cursor.fetchall()):
        return True
    cursor.execute("PRAGMA index_list(performance_metrics)")
    if any(row[1] == index_name for row in cursor.fetchall()):
        return True
    cursor.execute("PRAGMA index_list(chaos_events)")
    return any(row[1] == index_name for row in cursor.fetchall())


def _migration_add_wakatime_minutes(cursor: sqlite3.Cursor) -> None:
    """Add wakatime_minutes column to formation_logs if missing."""
    if not _column_exists(cursor, "formation_logs", "wakatime_minutes"):
        cursor.execute(
            "ALTER TABLE formation_logs ADD COLUMN wakatime_minutes INTEGER DEFAULT 0"
        )


def _migration_add_incident_srs_columns(cursor: sqlite3.Cursor) -> None:
    """Add SRS-related columns to incidents if missing."""
    if not _column_exists(cursor, "incidents", "resolution_score"):
        cursor.execute("ALTER TABLE incidents ADD COLUMN resolution_score INTEGER")
    if not _column_exists(cursor, "incidents", "next_review_date"):
        cursor.execute("ALTER TABLE incidents ADD COLUMN next_review_date TEXT")
    if not _column_exists(cursor, "incidents", "hints_used"):
        cursor.execute("ALTER TABLE incidents ADD COLUMN hints_used INTEGER DEFAULT 0")
    if not _column_exists(cursor, "incidents", "parent_incident_id"):
        cursor.execute("ALTER TABLE incidents ADD COLUMN parent_incident_id INTEGER")
    if not _column_exists(cursor, "incidents", "difficulty_level"):
        cursor.execute(
            "ALTER TABLE incidents ADD COLUMN difficulty_level INTEGER DEFAULT 1"
        )
    if not _column_exists(cursor, "incidents", "generated_by"):
        cursor.execute(
            "ALTER TABLE incidents ADD COLUMN generated_by TEXT DEFAULT 'template'"
        )


def _migration_add_indexes(cursor: sqlite3.Cursor) -> None:
    """Add indexes for common queries if missing."""
    if not _index_exists(cursor, "idx_incidents_status_timestamp"):
        cursor.execute(
            "CREATE INDEX idx_incidents_status_timestamp ON incidents(status, timestamp)"
        )
    if not _index_exists(cursor, "idx_incidents_review_status"):
        cursor.execute(
            "CREATE INDEX idx_incidents_review_status ON incidents(next_review_date, status)"
        )
    if not _index_exists(cursor, "idx_performance_metrics_timestamp"):
        cursor.execute(
            "CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics(timestamp)"
        )
    if not _index_exists(cursor, "idx_chaos_events_timestamp"):
        cursor.execute(
            "CREATE INDEX idx_chaos_events_timestamp ON chaos_events(timestamp)"
        )


def _migration_add_quiz_cards(cursor: sqlite3.Cursor) -> None:
    """Add quiz_cards table if missing."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            difficulty INTEGER,
            last_reviewed TEXT,
            review_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def _migration_add_learning_profile(cursor: sqlite3.Cursor) -> None:
    """Add user_learning_profile table if missing."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_learning_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            current_topics TEXT,
            recent_achievements TEXT,
            learning_difficulty TEXT
        );
        """
    )


def _migration_add_chaos_history(cursor: sqlite3.Cursor) -> None:
    """Add chaos_history table if missing."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chaos_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            template_name TEXT,
            attempt_date TEXT,
            user_answer TEXT,
            ai_feedback TEXT,
            success BOOLEAN
        );
        """
    )


def _cleanup_old_records(conn: sqlite3.Connection) -> None:
    """Optional data retention cleanup controlled by env variable.

    Set SKILLOPS_RETENTION_DAYS to enable cleanup.
    """
    run_on_start = os.getenv("SKILLOPS_RETENTION_RUN_ON_START", "false").lower()
    if run_on_start not in {"1", "true", "yes"}:
        return
    retention_raw = os.getenv("SKILLOPS_RETENTION_DAYS", "").strip()
    if not retention_raw:
        return
    try:
        retention_days = int(retention_raw)
    except ValueError:
        return
    if retention_days <= 0:
        return

    cleanup_old_records(retention_days=retention_days, connection=conn)


def cleanup_old_records(
    storage_path: Optional[Path] = None,
    retention_days: Optional[int] = None,
    vacuum: bool = False,
    connection: Optional[sqlite3.Connection] = None,
) -> int:
    """Run data retention cleanup and return number of rows deleted."""
    retention_raw = retention_days
    if retention_raw is None:
        raw_env = os.getenv("SKILLOPS_RETENTION_DAYS", "").strip()
        retention_raw = int(raw_env) if raw_env.isdigit() else None

    if not retention_raw or retention_raw <= 0:
        return 0

    conn = connection or get_connection(storage_path)
    cursor = conn.cursor()
    cutoff = f"-{retention_raw} days"

    total_deleted = 0

    cursor.execute(
        """
        DELETE FROM performance_metrics
        WHERE timestamp < datetime('now', ?)
        """,
        (cutoff,),
    )
    total_deleted += cursor.rowcount

    cursor.execute(
        """
        DELETE FROM chaos_events
        WHERE timestamp < datetime('now', ?)
        """,
        (cutoff,),
    )
    total_deleted += cursor.rowcount

    cursor.execute(
        """
        DELETE FROM incidents
        WHERE status = 'resolved'
          AND timestamp < datetime('now', ?)
        """,
        (cutoff,),
    )
    total_deleted += cursor.rowcount

    if connection is None:
        conn.commit()
        conn.close()

    if vacuum:
        vacuum_conn = get_connection(storage_path)
        vacuum_conn.execute("VACUUM")
        vacuum_conn.close()

    return total_deleted


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


def _migration_add_passive_tracking_tables(cursor: sqlite3.Cursor) -> None:
    """Add tables for passive tracking (Phase 3)."""
    # Code sessions from git hooks
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

    # Tracking summary (consolidated daily metrics)
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

    # Add indexes for performance
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_code_sessions_date ON code_sessions(date)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_tracking_summary_date ON tracking_summary(date)"
    )
