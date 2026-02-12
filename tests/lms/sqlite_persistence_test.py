"""Tests for SQLite persistence layer."""

import pytest

from src.lms.database import (
    get_connection,
    get_current_session_id,
    get_db_path,
    init_db,
)
from src.lms.persistence import (
    calculate_streak,
    get_completed_steps_for_today,
    get_context,
    get_daily_summary,
    mark_step_completed,
    save_cards_created,
    save_formation_log,
    set_context,
)


@pytest.fixture()
def sqlite_env(tmp_path, monkeypatch):
    """Initialize a temporary SQLite database for tests."""
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    init_db()
    yield


def _set_logical_date(monkeypatch, date_str: str) -> None:
    """Patch logical date helpers to return a fixed date."""
    monkeypatch.setattr("src.lms.database.get_logical_date", lambda: date_str)
    monkeypatch.setattr("src.lms.persistence.get_logical_date", lambda: date_str)


def test_get_db_path_uses_storage_env(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))

    db_path = get_db_path()

    assert db_path.parent == tmp_path
    assert db_path.name == "skillops.db"


def test_get_current_session_id_reuses_session(sqlite_env, monkeypatch):
    _ = sqlite_env
    _set_logical_date(monkeypatch, "2026-02-09")

    first_id = get_current_session_id()
    second_id = get_current_session_id()

    assert first_id == second_id


def test_set_context_upserts_value(sqlite_env):
    _ = sqlite_env
    set_context("focus", "docker")

    assert get_context("focus") == "docker"

    set_context("focus", "kubernetes")

    assert get_context("focus") == "kubernetes"


def test_mark_step_completed_records_steps(sqlite_env, monkeypatch):
    _ = sqlite_env
    _set_logical_date(monkeypatch, "2026-02-09")

    mark_step_completed(1)
    mark_step_completed(2)
    mark_step_completed(1)

    completed = get_completed_steps_for_today()

    assert set(completed) == {1, 2}


def test_get_daily_summary_aggregates_session_data(sqlite_env, monkeypatch):
    _ = sqlite_env
    date_str = "2026-02-09"
    _set_logical_date(monkeypatch, date_str)

    mark_step_completed(1)
    mark_step_completed(3)
    save_formation_log(["Goal 1"], "Solid recap.", 45)
    save_cards_created(7, source="create")

    summary = get_daily_summary(date_str)

    assert summary["date"] == date_str
    assert summary["steps_completed"] == 2
    assert set(summary["steps_list"]) == {1, 3}
    assert summary["total_time_minutes"] == 45
    assert summary["cards_created"] == 7


def test_calculate_streak_counts_consecutive_days(sqlite_env, monkeypatch):
    _ = sqlite_env
    _set_logical_date(monkeypatch, "2026-02-10")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO sessions (date) VALUES (?)",
        [
            ("2026-02-10",),
            ("2026-02-09",),
            ("2026-02-08",),
            ("2026-02-07",),
            ("2026-02-06",),
        ],
    )
    conn.commit()
    conn.close()

    assert calculate_streak() == 5


def test_schema_version_table_created(sqlite_env):
    _ = sqlite_env
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    )
    row = cursor.fetchone()
    conn.close()
    assert row is not None


def test_schema_version_has_latest(sqlite_env):
    _ = sqlite_env
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(version) FROM schema_version")
    version = cursor.fetchone()[0]
    conn.close()
    assert version >= 2
