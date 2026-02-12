"""Tests for Phase 6 predictive analytics."""

from datetime import datetime, timedelta

from src.lms.database import get_connection, init_db
from src.lms.predictive_analytics import (
    calculate_activity_streak,
    detect_anomalies,
    forecast_weekly_time,
    generate_predictive_insights,
    get_tracking_series,
    predict_next_study_date,
)


def _insert_tracking_summary(conn, date_str, seconds, commits):
    conn.execute(
        """
        INSERT OR REPLACE INTO tracking_summary
        (date, wakatime_seconds, git_commits, git_files_changed,
         git_lines_added, git_lines_deleted, activity_level)
        VALUES (?, ?, ?, 0, 0, 0, ?)
        """,
        (date_str, seconds, commits, "medium"),
    )
    conn.commit()


def test_get_tracking_series(tmp_path, monkeypatch):
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    try:
        _insert_tracking_summary(conn, "2026-02-10", 3600, 2)
    finally:
        conn.close()
    monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

    series = get_tracking_series(days=7, storage_path=tmp_path)
    assert len(series) >= 1


def test_calculate_activity_streak():
    series = [
        {"date": "2026-02-10", "wakatime_seconds": 0, "git_commits": 0},
        {"date": "2026-02-11", "wakatime_seconds": 3600, "git_commits": 1},
        {"date": "2026-02-12", "wakatime_seconds": 1200, "git_commits": 0},
    ]
    assert calculate_activity_streak(series) == 2


def test_predict_next_study_date():
    series = [
        {"date": "2026-02-10", "wakatime_seconds": 3600, "git_commits": 1},
        {"date": "2026-02-12", "wakatime_seconds": 3600, "git_commits": 1},
    ]
    assert predict_next_study_date(series) == "2026-02-14"


def test_forecast_weekly_time_increasing():
    series = []
    for i in range(7):
        series.append(
            {
                "date": f"2026-02-{10+i}",
                "wakatime_seconds": 1000 + i * 100,
                "git_commits": 1,
            }
        )
    forecast = forecast_weekly_time(series)
    assert forecast.forecast_total_next_week >= 0


def test_detect_anomalies():
    series = []
    for i in range(10):
        series.append(
            {
                "date": (datetime(2026, 2, 1) + timedelta(days=i)).strftime("%Y-%m-%d"),
                "wakatime_seconds": 1000,
                "git_commits": 1,
            }
        )
    series.append(
        {
            "date": "2026-02-20",
            "wakatime_seconds": 20000,
            "git_commits": 1,
        }
    )
    anomalies = detect_anomalies(series)
    assert any(a.metric == "wakatime_seconds" for a in anomalies)


def test_generate_predictive_insights(tmp_path, monkeypatch):
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    try:
        _insert_tracking_summary(conn, "2026-02-10", 3600, 2)
        _insert_tracking_summary(conn, "2026-02-11", 1800, 1)
    finally:
        conn.close()
    monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

    insights = generate_predictive_insights(days=7, storage_path=tmp_path)
    assert insights["series_count"] >= 1
    assert "forecast_total_next_week_seconds" in insights
