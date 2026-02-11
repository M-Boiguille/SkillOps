"""Data Access Layer for SkillOps using SQLite."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any

from .database import get_connection, get_current_session_id, get_logical_date

# --- Context Management ---


def set_context(key: str, value: str):
    """Set a context value (upsert)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO context (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_context(key: str) -> Optional[str]:
    """Get a context value."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM context WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# --- Step Completion ---


def mark_step_completed(step_number: int):
    """Mark a step as completed for the current session."""
    session_id = get_current_session_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO step_completions (session_id, step_number) VALUES (?, ?)",
        (session_id, step_number),
    )
    conn.commit()
    conn.close()


def get_completed_steps_for_today() -> List[int]:
    """Get list of completed step numbers for the current session."""
    session_id = get_current_session_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT step_number FROM step_completions WHERE session_id = ?", (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


# --- Formation ---


def save_formation_log(
    goals: List[str],
    recall: str,
    duration_minutes: int,
    wakatime_minutes: Optional[int] = None,
):
    """Save formation session log."""
    session_id = get_current_session_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO formation_logs (session_id, goals, recall, "
        "duration_minutes, wakatime_minutes) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            session_id,
            json.dumps(goals),
            recall,
            duration_minutes,
            int(wakatime_minutes or 0),
        ),
    )
    conn.commit()
    conn.close()


# --- Reinforce ---


def save_reinforce_progress(
    exercise_id: str,
    title: str,
    duration: int,
    completed: bool,
    quality: int,
    srs_data: Dict,
):
    """Save reinforce exercise progress."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO reinforce_progress
        (exercise_id, title, duration_seconds, completed, quality, srs_data)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (exercise_id, title, duration, completed, quality, json.dumps(srs_data)),
    )
    conn.commit()
    conn.close()


def get_reinforce_history(exercise_id: str) -> List[Dict]:
    """Get history for a specific exercise."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reinforce_progress WHERE exercise_id = ? ORDER BY timestamp DESC",
        (exercise_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        # id, exercise_id, title, duration, completed, quality, timestamp, srs_data
        history.append(
            {
                "id": row[0],
                "exercise_id": row[1],
                "title": row[2],
                "duration_seconds": row[3],
                "completed": bool(row[4]),
                "quality": row[5],
                "timestamp": row[6],
                "srs_data": json.loads(row[7]) if row[7] else {},
            }
        )
    return history


def get_latest_reinforce_progress(exercise_id: str) -> Optional[Dict]:
    """Get the most recent progress for an exercise."""
    history = get_reinforce_history(exercise_id)
    return history[0] if history else None


# --- Cards ---


def save_cards_created(count: int, source: str = "manual"):
    """Log created flashcards."""
    session_id = get_current_session_id()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO card_creations (session_id, count, source) VALUES (?, ?, ?)",
        (session_id, count, source),
    )
    conn.commit()
    conn.close()


def get_progress_history(storage_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return daily progress summaries as a list ordered by date."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM sessions ORDER BY date")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()

    history: List[Dict[str, Any]] = []
    for date_str in dates:
        summary = get_daily_summary(date_str, storage_path)
        if summary:
            history.append(
                {
                    "date": summary.get("date"),
                    "steps": summary.get("steps_completed", 0),
                    "time": summary.get("total_time_minutes", 0),
                    "cards": summary.get("cards_created", 0),
                }
            )
    return history


# --- Metrics / Review ---


def get_daily_summary(date_str: str, storage_path: Optional[Path] = None) -> Dict:
    """Get summary metrics for a specific date."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    # Get session ID for date
    cursor.execute("SELECT id FROM sessions WHERE date = ?", (date_str,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {}

    session_id = row[0]

    # Steps
    cursor.execute(
        "SELECT step_number FROM step_completions WHERE session_id = ?", (session_id,)
    )
    steps = [r[0] for r in cursor.fetchall()]

    # Formation time
    cursor.execute(
        "SELECT SUM(duration_minutes), SUM(wakatime_minutes) "
        "FROM formation_logs WHERE session_id = ?",
        (session_id,),
    )
    formation_row = cursor.fetchone() or (0, 0)
    formation_time = formation_row[0] or 0
    wakatime_time = formation_row[1] or 0

    # Reinforce time (approximate, filtered by timestamp date)
    cursor.execute(
        "SELECT SUM(duration_seconds) FROM reinforce_progress WHERE date(timestamp) = ?",
        (date_str,),
    )
    reinforce_time_sec = cursor.fetchone()[0] or 0

    # Cards
    cursor.execute(
        "SELECT SUM(count) FROM card_creations WHERE session_id = ?", (session_id,)
    )
    cards_created = cursor.fetchone()[0] or 0

    formation_minutes = wakatime_time if wakatime_time > 0 else formation_time
    total_time_minutes = formation_minutes + (reinforce_time_sec // 60)

    step_durations = get_step_durations_for_date(date_str, storage_path)

    conn.close()

    return {
        "date": date_str,
        "steps_completed": len(steps),
        "steps_list": steps,
        "total_time_minutes": total_time_minutes,
        "cards_created": cards_created,
        "step_durations": step_durations,
    }


def get_step_durations_for_date(
    date_str: str, storage_path: Optional[Path] = None
) -> Dict[int, int]:
    """Return step execution durations (seconds) for a given date."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT step_id, SUM(duration_seconds) "
        "FROM performance_metrics "
        "WHERE date(timestamp) = ? AND step_id LIKE 'step_%' "
        "GROUP BY step_id",
        (date_str,),
    )
    rows = cursor.fetchall()
    conn.close()

    durations: Dict[int, int] = {}
    for step_id, total_seconds in rows:
        try:
            step_number = int(str(step_id).replace("step_", ""))
        except ValueError:
            continue
        durations[step_number] = int(total_seconds or 0)
    return durations


def calculate_streak(storage_path: Optional[Path] = None) -> int:
    """Calculate current streak from sessions."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM sessions ORDER BY date DESC")
    dates = [r[0] for r in cursor.fetchall()]
    conn.close()

    if not dates:
        return 0

    streak = 0
    check_date = datetime.strptime(get_logical_date(), "%Y-%m-%d")

    # If most recent session is not today or yesterday, streak is broken (0)
    last_session_date = datetime.strptime(dates[0], "%Y-%m-%d")
    diff = (check_date - last_session_date).days
    if diff > 1:
        return 0

    # Count backwards
    for date_str in dates:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        if d == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        elif d > check_date:
            continue  # Should not happen if sorted desc
        else:
            break  # Gap found

    return streak
