"""Phase 6 predictive analytics utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean, pstdev
from typing import Dict, List, Optional

from src.lms.database import get_connection, get_logical_date


@dataclass
class TrendForecast:
    slope_per_day: float
    forecast_total_next_week: float


@dataclass
class Anomaly:
    date: str
    metric: str
    value: float
    z_score: float


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_tracking_series(
    days: int = 30, storage_path: Optional[Path] = None
) -> List[Dict]:
    """Fetch recent tracking_summary rows (ascending by date)."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    today = _parse_date(get_logical_date())
    start_date = today - timedelta(days=days - 1)
    cursor.execute(
        """
        SELECT date, wakatime_seconds, git_commits
        FROM tracking_summary
        WHERE date >= ?
        ORDER BY date ASC
        """,
        (start_date.strftime("%Y-%m-%d"),),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "date": row[0],
            "wakatime_seconds": row[1],
            "git_commits": row[2],
        }
        for row in rows
    ]


def calculate_activity_streak(series: List[Dict]) -> int:
    """Calculate current streak of days with activity (time or commits)."""
    if not series:
        return 0
    streak = 0
    for entry in reversed(series):
        if (entry["wakatime_seconds"] or 0) > 0 or (entry["git_commits"] or 0) > 0:
            streak += 1
        else:
            break
    return streak


def predict_next_study_date(series: List[Dict]) -> Optional[str]:
    """Predict the next study date based on average gap between active days."""
    if len(series) < 2:
        return None

    active_dates = [
        _parse_date(entry["date"])
        for entry in series
        if (entry["wakatime_seconds"] or 0) > 0 or (entry["git_commits"] or 0) > 0
    ]
    if len(active_dates) < 2:
        return None

    active_dates.sort()
    gaps = [
        (active_dates[i] - active_dates[i - 1]).days
        for i in range(1, len(active_dates))
    ]
    avg_gap = max(1, round(mean(gaps)))
    next_date = active_dates[-1] + timedelta(days=avg_gap)
    return next_date.strftime("%Y-%m-%d")


def forecast_weekly_time(series: List[Dict]) -> TrendForecast:
    """Forecast next-week total coding time using a simple linear trend."""
    if not series:
        return TrendForecast(slope_per_day=0.0, forecast_total_next_week=0.0)

    y_values = [entry["wakatime_seconds"] for entry in series]
    n = len(y_values)
    x_values = list(range(n))
    x_mean = mean(x_values)
    y_mean = mean(y_values)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values) or 1
    slope = numerator / denominator

    next_week_total = 0.0
    for i in range(n, n + 7):
        predicted = y_mean + slope * (i - x_mean)
        next_week_total += max(0.0, predicted)

    return TrendForecast(slope_per_day=slope, forecast_total_next_week=next_week_total)


def detect_anomalies(series: List[Dict], z_threshold: float = 2.0) -> List[Anomaly]:
    """Detect anomaly days using z-score for time and commits."""
    if len(series) < 2:
        return []

    times = [entry["wakatime_seconds"] for entry in series]
    commits = [entry["git_commits"] for entry in series]
    time_mean = mean(times)
    commit_mean = mean(commits)
    time_std = pstdev(times) or 1.0
    commit_std = pstdev(commits) or 1.0

    anomalies: List[Anomaly] = []
    for entry in series:
        time_z = (entry["wakatime_seconds"] - time_mean) / time_std
        commit_z = (entry["git_commits"] - commit_mean) / commit_std
        if abs(time_z) >= z_threshold:
            anomalies.append(
                Anomaly(
                    date=entry["date"],
                    metric="wakatime_seconds",
                    value=float(entry["wakatime_seconds"]),
                    z_score=float(time_z),
                )
            )
        if abs(commit_z) >= z_threshold:
            anomalies.append(
                Anomaly(
                    date=entry["date"],
                    metric="git_commits",
                    value=float(entry["git_commits"]),
                    z_score=float(commit_z),
                )
            )
    return anomalies


def generate_predictive_insights(
    days: int = 30, storage_path: Optional[Path] = None
) -> Dict:
    """Generate predictive insights from tracking data."""
    series = get_tracking_series(days=days, storage_path=storage_path)
    forecast = forecast_weekly_time(series)
    next_date = predict_next_study_date(series)
    anomalies = detect_anomalies(series)
    streak = calculate_activity_streak(series)

    return {
        "series_count": len(series),
        "streak": streak,
        "next_study_date": next_date,
        "forecast_total_next_week_seconds": forecast.forecast_total_next_week,
        "slope_per_day": forecast.slope_per_day,
        "anomalies": anomalies,
    }
