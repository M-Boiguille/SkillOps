"""Tests for SQLite progress history helpers."""

from src.lms.database import get_connection, init_db
from src.lms.persistence import get_progress_history


def test_get_progress_history_empty(tmp_path):
    init_db(tmp_path)

    assert get_progress_history(tmp_path) == []


def test_get_progress_history_returns_daily_summaries(tmp_path):
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO sessions (date) VALUES (?)", ("2026-01-09",))
    cursor.execute("INSERT INTO sessions (date) VALUES (?)", ("2026-01-10",))

    cursor.execute("SELECT id FROM sessions WHERE date = ?", ("2026-01-09",))
    session1 = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM sessions WHERE date = ?", ("2026-01-10",))
    session2 = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO step_completions (session_id, step_number) VALUES (?, ?)",
        (session1, 1),
    )
    cursor.execute(
        "INSERT INTO formation_logs (session_id, goals, recall, "
        "duration_minutes) VALUES (?, ?, ?, ?)",
        (session1, "[]", "", 30),
    )
    cursor.execute(
        "INSERT INTO card_creations (session_id, count, source) VALUES (?, ?, ?)",
        (session1, 5, "test"),
    )

    cursor.execute(
        "INSERT INTO step_completions (session_id, step_number) VALUES (?, ?)",
        (session2, 2),
    )
    cursor.execute(
        "INSERT INTO formation_logs (session_id, goals, recall, "
        "duration_minutes) VALUES (?, ?, ?, ?)",
        (session2, "[]", "", 45),
    )

    conn.commit()
    conn.close()

    history = get_progress_history(tmp_path)

    assert history == [
        {"date": "2026-01-09", "steps": 1, "time": 30, "cards": 5},
        {"date": "2026-01-10", "steps": 1, "time": 45, "cards": 0},
    ]
