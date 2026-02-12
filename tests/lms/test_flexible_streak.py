"""Test flexible streak calculation logic."""

from datetime import datetime, timedelta
import pytest
import os
from pathlib import Path

from src.lms.persistence import calculate_streak
from src.lms.database import init_db, get_connection


@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary storage for testing."""
    storage_path = tmp_path / "skillops_test"
    storage_path.mkdir()
    # Point to temp storage
    os.environ["SKILLOPS_STORAGE_PATH"] = str(storage_path)
    yield storage_path
    # Cleanup
    if "SKILLOPS_STORAGE_PATH" in os.environ:
        del os.environ["SKILLOPS_STORAGE_PATH"]


def add_session_date(storage_path: Path, date_str: str) -> None:
    """Helper to add a session for a specific date."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO sessions (date) VALUES (?)", (date_str,))
    conn.commit()
    conn.close()


def test_streak_no_activity(temp_storage):
    """Test streak is 0 when no activity."""
    init_db(temp_storage)
    assert calculate_streak(temp_storage) == 0


def test_streak_activity_today(temp_storage):
    """Test streak counts today's activity (with 5 days in last 8)."""
    init_db(temp_storage)
    today = datetime.now().date()

    # Need 5 days active in last 8 to have a streak
    # Days: today + 4 others (2 rest days allowed)
    active_days = [0, 1, 3, 4, 6]  # Days 2 and 5 are rest
    for i in active_days:
        add_session_date(temp_storage, (today - timedelta(days=i)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak > 0, "Should have streak with 5 active days in last 8"


def test_streak_allows_one_rest_day(temp_storage):
    """Test streak survives 1 rest day (with 5 days in last 8)."""
    init_db(temp_storage)
    today = datetime.now().date()

    # 5 active days with 1 rest day gap
    active_days = [0, 1, 3, 4, 6]  # Day 2 has 1 day rest
    for i in active_days:
        add_session_date(temp_storage, (today - timedelta(days=i)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak > 0, "Streak should survive 1 rest day"


def test_streak_allows_two_consecutive_rest_days(temp_storage):
    """Test streak survives 2 consecutive rest days (with 5 days in last 8)."""
    init_db(temp_storage)
    today = datetime.now().date()

    # 5 active days with 2 consecutive rest days
    active_days = [0, 1, 4, 5, 7]  # Days 2-3 have 2 rest days, day 6 is rest
    for i in active_days:
        add_session_date(temp_storage, (today - timedelta(days=i)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak > 0, "Streak should survive 2 consecutive rest days"


def test_streak_breaks_after_three_consecutive_rest_days(temp_storage):
    """Test streak breaks after 3 consecutive rest days."""
    init_db(temp_storage)
    today = datetime.now().date()

    # Activity 4+ days ago (3+ consecutive rest days with no recent activity)
    add_session_date(temp_storage, (today - timedelta(days=4)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak == 0, "Streak should break after 3+ days of inactivity"


def test_streak_requires_min_5_days_in_last_8(temp_storage):
    """Test streak requires at least 5 active days in last 8 days."""
    init_db(temp_storage)
    today = datetime.now().date()

    # Only 4 days active in last 8 days
    for i in [0, 1, 3, 5]:
        add_session_date(temp_storage, (today - timedelta(days=i)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak == 0, "Streak should be 0 if less than 5 active days in last 8 days"


def test_streak_valid_with_5_active_days_in_last_8(temp_storage):
    """Test streak is valid with exactly 5 active days in last 8 days."""
    init_db(temp_storage)
    today = datetime.now().date()

    # 5 days active in last 8 days with max 2 consecutive rest
    days_active = [0, 1, 3, 4, 6]  # Days 2 and 5 are rest
    for i in days_active:
        add_session_date(temp_storage, (today - timedelta(days=i)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak > 0, "Streak should be valid with 5 active days in last 8 days"


def test_streak_no_activity_in_last_3_days(temp_storage):
    """Test streak breaks if no activity in last 3 days."""
    init_db(temp_storage)
    today = datetime.now().date()

    # Activity 4+ days ago
    add_session_date(temp_storage, (today - timedelta(days=4)).strftime("%Y-%m-%d"))
    add_session_date(temp_storage, (today - timedelta(days=5)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak == 0, "Streak should break if no activity in last 3 days"


def test_streak_continuous_perfect_streak(temp_storage):
    """Test streak with continuous daily activity."""
    init_db(temp_storage)
    today = datetime.now().date()

    # Daily activity for 10 days
    for i in range(10):
        add_session_date(temp_storage, (today - timedelta(days=i)).strftime("%Y-%m-%d"))

    streak = calculate_streak(temp_storage)
    assert streak >= 10, "Continuous daily activity should give streak of at least 10"
