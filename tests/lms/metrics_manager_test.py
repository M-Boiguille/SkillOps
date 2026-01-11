"""
Test suite for MetricsManager class.

Based on:
- URD (User Requirements Document) - US-002: Review des Métriques Quotidiennes
- Sprint Planning Sprint 1 - Task T010-4: Implémenter métriques agrégées
- ADR-004: Persistence des Données (JSON/YAML local)

MetricsManager responsibilities:
1. Calculate streak (consecutive days of activity)
2. Calculate average time per day
3. Calculate total cards created
4. Update aggregated metrics from progress history
5. Provide metrics for Review step display
"""

import pytest
from pathlib import Path
from datetime import date, timedelta
import json
from src.lms.persistence import MetricsManager
from src.lms.persistence import ProgressManager


class TestMetricsManagerInit:
    """Test MetricsManager initialization and configuration."""

    def test_init_with_valid_path(self, tmp_path):
        """GIVEN a valid file path
        WHEN MetricsManager is initialized
        THEN it should create instance with correct file_path
        """
        metrics_file = tmp_path / "test_metrics.json"
        manager = MetricsManager(metrics_file)

        assert manager.file_path == metrics_file
        assert isinstance(manager.file_path, Path)

    def test_init_creates_parent_directory(self, tmp_path):
        """GIVEN a path with non-existent parent directories
        WHEN MetricsManager is initialized and save is called
        THEN parent directories should be created automatically
        """
        nested_path = tmp_path / "storage" / "nested" / "metrics.json"
        manager = MetricsManager(nested_path)

        # Trigger directory creation by saving
        manager.current_metrics = {"streak": 0, "avg_time": 0.0, "total_cards": 0}
        manager.save_metrics()

        assert nested_path.parent.exists()
        assert nested_path.exists()

    def test_init_with_string_path(self, tmp_path):
        """GIVEN a string path instead of Path object
        WHEN MetricsManager is initialized
        THEN it should convert to Path and work correctly
        """
        metrics_file = str(tmp_path / "metrics.json")
        manager = MetricsManager(metrics_file)

        assert isinstance(manager.file_path, Path)
        assert manager.file_path.name == "metrics.json"


class TestLoadMetrics:
    """Test loading metrics from JSON file."""

    def test_load_existing_metrics(self, tmp_path):
        """GIVEN an existing metrics file with valid data
        WHEN load_metrics is called
        THEN it should return the metrics dict
        """
        metrics_file = tmp_path / "metrics.json"
        test_data = {"streak": 15, "avg_time": 3.5, "total_cards": 120}
        metrics_file.write_text(json.dumps(test_data))

        manager = MetricsManager(metrics_file)
        loaded = manager.load_metrics()

        assert loaded == test_data
        assert loaded["streak"] == 15
        assert loaded["avg_time"] == 3.5
        assert loaded["total_cards"] == 120

    def test_load_nonexistent_file_returns_default(self, tmp_path):
        """GIVEN a non-existent metrics file
        WHEN load_metrics is called
        THEN it should return default metrics (zeros)
        """
        metrics_file = tmp_path / "nonexistent.json"
        manager = MetricsManager(metrics_file)

        loaded = manager.load_metrics()

        assert loaded == {"streak": 0, "avg_time": 0.0, "total_cards": 0}
        assert isinstance(loaded["streak"], int)
        assert isinstance(loaded["avg_time"], float)
        assert isinstance(loaded["total_cards"], int)

    def test_load_malformed_json_returns_default(self, tmp_path):
        """GIVEN a metrics file with malformed JSON
        WHEN load_metrics is called
        THEN it should return default metrics and not crash
        """
        metrics_file = tmp_path / "malformed.json"
        metrics_file.write_text("{invalid json content")

        manager = MetricsManager(metrics_file)
        loaded = manager.load_metrics()

        assert loaded == {"streak": 0, "avg_time": 0.0, "total_cards": 0}

    def test_load_empty_file_returns_default(self, tmp_path):
        """GIVEN an empty metrics file
        WHEN load_metrics is called
        THEN it should return default metrics
        """
        metrics_file = tmp_path / "empty.json"
        metrics_file.write_text("")

        manager = MetricsManager(metrics_file)
        loaded = manager.load_metrics()

        assert loaded == {"streak": 0, "avg_time": 0.0, "total_cards": 0}

    def test_load_partial_metrics_fills_missing(self, tmp_path):
        """GIVEN a metrics file with missing fields
        WHEN load_metrics is called
        THEN it should fill missing fields with defaults
        """
        metrics_file = tmp_path / "partial.json"
        partial_data = {"streak": 10}  # Missing avg_time and total_cards
        metrics_file.write_text(json.dumps(partial_data))

        manager = MetricsManager(metrics_file)
        loaded = manager.load_metrics()

        assert loaded["streak"] == 10
        assert "avg_time" in loaded
        assert "total_cards" in loaded


class TestSaveMetrics:
    """Test saving metrics to JSON file."""

    def test_save_metrics_creates_file(self, tmp_path):
        """GIVEN metrics data
        WHEN save_metrics is called
        THEN it should create the file with correct data
        """
        metrics_file = tmp_path / "metrics.json"
        manager = MetricsManager(metrics_file)

        manager.current_metrics = {"streak": 20, "avg_time": 4.2, "total_cards": 150}
        manager.save_metrics()

        assert metrics_file.exists()
        saved_data = json.loads(metrics_file.read_text())
        assert saved_data == manager.current_metrics

    def test_save_metrics_overwrites_existing(self, tmp_path):
        """GIVEN an existing metrics file
        WHEN save_metrics is called with new data
        THEN it should overwrite with new values
        """
        metrics_file = tmp_path / "metrics.json"
        old_data = {"streak": 5, "avg_time": 2.0, "total_cards": 50}
        metrics_file.write_text(json.dumps(old_data))

        manager = MetricsManager(metrics_file)
        manager.current_metrics = {"streak": 10, "avg_time": 3.0, "total_cards": 100}
        manager.save_metrics()

        saved_data = json.loads(metrics_file.read_text())
        assert saved_data["streak"] == 10
        assert saved_data != old_data

    def test_save_metrics_pretty_format(self, tmp_path):
        """GIVEN metrics data
        WHEN save_metrics is called
        THEN JSON should be saved with indentation for readability
        """
        metrics_file = tmp_path / "metrics.json"
        manager = MetricsManager(metrics_file)

        manager.current_metrics = {"streak": 1, "avg_time": 1.0, "total_cards": 1}
        manager.save_metrics()

        content = metrics_file.read_text()
        assert "\n" in content  # Should have newlines (pretty printed)
        assert "  " in content or "\t" in content  # Should have indentation


class TestCalculateStreak:
    """Test streak calculation logic (consecutive days)."""

    def test_calculate_streak_no_progress(self, tmp_path):
        """GIVEN no progress data
        WHEN calculate_streak is called
        THEN streak should be 0
        """
        progress_file = tmp_path / "progress.json"
        progress_file.write_text("[]")

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        streak = metrics_mgr.calculate_streak(progress_mgr.load_progress())

        assert streak == 0

    def test_calculate_streak_single_day(self, tmp_path):
        """GIVEN progress for only today
        WHEN calculate_streak is called
        THEN streak should be 1
        """
        today = date.today().strftime("%Y-%m-%d")
        progress_file = tmp_path / "progress.json"
        progress_data = [{"date": today, "steps": 8, "time": 3.5, "cards": 10}]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        streak = metrics_mgr.calculate_streak(progress_mgr.load_progress())

        assert streak == 1

    def test_calculate_streak_consecutive_days(self, tmp_path):
        """GIVEN progress for 5 consecutive days ending today
        WHEN calculate_streak is called
        THEN streak should be 5
        """
        progress_file = tmp_path / "progress.json"
        progress_data = []

        # Create 5 consecutive days of progress ending today
        for i in range(5):
            day = date.today() - timedelta(days=4 - i)
            progress_data.append(
                {"date": day.strftime("%Y-%m-%d"), "steps": 7, "time": 3.0, "cards": 8}
            )

        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        streak = metrics_mgr.calculate_streak(progress_mgr.load_progress())

        assert streak == 5

    def test_calculate_streak_broken_by_gap(self, tmp_path):
        """GIVEN progress with a gap (missing day)
        WHEN calculate_streak is called
        THEN streak should only count from last gap
        """
        progress_file = tmp_path / "progress.json"
        today = date.today()

        progress_data = [
            # Old streak (should be ignored)
            {
                "date": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
                "steps": 8,
                "time": 3.0,
                "cards": 10,
            },
            {
                "date": (today - timedelta(days=9)).strftime("%Y-%m-%d"),
                "steps": 8,
                "time": 3.0,
                "cards": 10,
            },
            # Gap here (day 8, 7, 6, 5, 4)
            # Current streak
            {
                "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
                "steps": 7,
                "time": 2.5,
                "cards": 8,
            },
            {
                "date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                "steps": 8,
                "time": 3.0,
                "cards": 9,
            },
            {
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "steps": 7,
                "time": 2.8,
                "cards": 7,
            },
            {"date": today.strftime("%Y-%m-%d"), "steps": 8, "time": 3.2, "cards": 10},
        ]

        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        streak = metrics_mgr.calculate_streak(progress_mgr.load_progress())

        assert streak == 4  # Only counts last 4 consecutive days

    def test_calculate_streak_not_including_today(self, tmp_path):
        """GIVEN progress ending yesterday (no activity today)
        WHEN calculate_streak is called
        THEN streak should still count yesterday's consecutive days
        """
        progress_file = tmp_path / "progress.json"
        yesterday = date.today() - timedelta(days=1)

        progress_data = []
        for i in range(3):
            day = yesterday - timedelta(days=2 - i)
            progress_data.append(
                {"date": day.strftime("%Y-%m-%d"), "steps": 7, "time": 3.0, "cards": 8}
            )

        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        streak = metrics_mgr.calculate_streak(progress_mgr.load_progress())

        assert streak == 3

    def test_calculate_streak_unsorted_data(self, tmp_path):
        """GIVEN progress data in random order
        WHEN calculate_streak is called
        THEN it should handle sorting and calculate correctly
        """
        progress_file = tmp_path / "progress.json"
        today = date.today()

        # Intentionally unsorted
        progress_data = [
            {"date": today.strftime("%Y-%m-%d"), "steps": 8, "time": 3.0, "cards": 10},
            {
                "date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
                "steps": 7,
                "time": 2.5,
                "cards": 8,
            },
            {
                "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
                "steps": 8,
                "time": 3.2,
                "cards": 9,
            },
        ]

        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        streak = metrics_mgr.calculate_streak(progress_mgr.load_progress())

        assert streak == 3


class TestGetAverageTime:
    """Test average time calculation."""

    def test_get_average_time_no_data(self, tmp_path):
        """GIVEN no progress data
        WHEN get_average_time is called
        THEN it should return 0.0
        """
        progress_file = tmp_path / "progress.json"
        progress_file.write_text("[]")

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        avg = metrics_mgr.get_average_time(progress_mgr.load_progress())

        assert avg == 0.0
        assert isinstance(avg, float)

    def test_get_average_time_single_entry(self, tmp_path):
        """GIVEN progress with one entry
        WHEN get_average_time is called
        THEN average should equal that entry's time
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [{"date": "2026-01-10", "steps": 8, "time": 3.5, "cards": 10}]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        avg = metrics_mgr.get_average_time(progress_mgr.load_progress())

        assert avg == 3.5

    def test_get_average_time_multiple_entries(self, tmp_path):
        """GIVEN progress with multiple entries
        WHEN get_average_time is called
        THEN it should return correct average
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [
            {"date": "2026-01-08", "steps": 8, "time": 2.0, "cards": 10},
            {"date": "2026-01-09", "steps": 7, "time": 3.0, "cards": 8},
            {"date": "2026-01-10", "steps": 8, "time": 4.0, "cards": 12},
        ]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        avg = metrics_mgr.get_average_time(progress_mgr.load_progress())

        # (2.0 + 3.0 + 4.0) / 3 = 3.0
        assert avg == 3.0

    def test_get_average_time_rounds_to_decimal(self, tmp_path):
        """GIVEN progress with values that don't divide evenly
        WHEN get_average_time is called
        THEN result should be properly rounded float
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [
            {"date": "2026-01-08", "steps": 8, "time": 2.5, "cards": 10},
            {"date": "2026-01-09", "steps": 7, "time": 3.2, "cards": 8},
            {"date": "2026-01-10", "steps": 8, "time": 3.8, "cards": 12},
        ]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        avg = metrics_mgr.get_average_time(progress_mgr.load_progress())

        # (2.5 + 3.2 + 3.8) / 3 = 3.166...
        assert isinstance(avg, float)
        assert 3.16 <= avg <= 3.17  # Allow small floating point variance

    def test_get_average_time_last_n_days(self, tmp_path):
        """GIVEN progress spanning many days
        WHEN get_average_time is called with last_n_days parameter
        THEN it should only average recent days
        """
        progress_file = tmp_path / "progress.json"
        today = date.today()

        progress_data = []
        times = [1.0, 2.0, 3.0, 4.0, 5.0]  # 5 days
        for i, time_val in enumerate(times):
            day = today - timedelta(days=4 - i)
            progress_data.append(
                {
                    "date": day.strftime("%Y-%m-%d"),
                    "steps": 7,
                    "time": time_val,
                    "cards": 8,
                }
            )

        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        # Average last 3 days: (3.0 + 4.0 + 5.0) / 3 = 4.0
        avg = metrics_mgr.get_average_time(progress_mgr.load_progress(), last_n_days=3)

        assert avg == 4.0


class TestGetTotalCards:
    """Test total cards calculation."""

    def test_get_total_cards_no_data(self, tmp_path):
        """GIVEN no progress data
        WHEN get_total_cards is called
        THEN it should return 0
        """
        progress_file = tmp_path / "progress.json"
        progress_file.write_text("[]")

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        total = metrics_mgr.get_total_cards(progress_mgr.load_progress())

        assert total == 0
        assert isinstance(total, int)

    def test_get_total_cards_single_entry(self, tmp_path):
        """GIVEN progress with one entry
        WHEN get_total_cards is called
        THEN it should return that entry's cards count
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [{"date": "2026-01-10", "steps": 8, "time": 3.5, "cards": 15}]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        total = metrics_mgr.get_total_cards(progress_mgr.load_progress())

        assert total == 15

    def test_get_total_cards_multiple_entries(self, tmp_path):
        """GIVEN progress with multiple entries
        WHEN get_total_cards is called
        THEN it should return sum of all cards
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [
            {"date": "2026-01-08", "steps": 8, "time": 2.0, "cards": 10},
            {"date": "2026-01-09", "steps": 7, "time": 3.0, "cards": 12},
            {"date": "2026-01-10", "steps": 8, "time": 4.0, "cards": 8},
        ]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        total = metrics_mgr.get_total_cards(progress_mgr.load_progress())

        # 10 + 12 + 8 = 30
        assert total == 30

    def test_get_total_cards_large_dataset(self, tmp_path):
        """GIVEN progress for an entire year (365 days)
        WHEN get_total_cards is called
        THEN it should correctly sum all cards
        """
        progress_file = tmp_path / "progress.json"
        progress_data = []

        # Create 1 year of data (365 days, 10 cards per day)
        today = date.today()
        for i in range(365):
            day = today - timedelta(days=364 - i)
            progress_data.append(
                {"date": day.strftime("%Y-%m-%d"), "steps": 7, "time": 3.0, "cards": 10}
            )

        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        total = metrics_mgr.get_total_cards(progress_mgr.load_progress())

        assert total == 3650  # 365 days * 10 cards


class TestUpdateMetrics:
    """Test update_metrics method that refreshes all metrics."""

    def test_update_metrics_from_empty(self, tmp_path):
        """GIVEN no existing metrics and no progress
        WHEN update_metrics is called
        THEN all metrics should be initialized to zero
        """
        progress_file = tmp_path / "progress.json"
        progress_file.write_text("[]")
        metrics_file = tmp_path / "metrics.json"

        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        metrics_mgr.update_metrics(progress_mgr.load_progress())

        assert metrics_mgr.current_metrics["streak"] == 0
        assert metrics_mgr.current_metrics["avg_time"] == 0.0
        assert metrics_mgr.current_metrics["total_cards"] == 0

    def test_update_metrics_calculates_all(self, tmp_path):
        """GIVEN progress data
        WHEN update_metrics is called
        THEN all metrics should be calculated and saved
        """
        progress_file = tmp_path / "progress.json"
        today = date.today()

        progress_data = []
        for i in range(7):  # 7 consecutive days
            day = today - timedelta(days=6 - i)
            progress_data.append(
                {"date": day.strftime("%Y-%m-%d"), "steps": 8, "time": 3.0, "cards": 10}
            )

        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        metrics_mgr.update_metrics(progress_mgr.load_progress())

        assert metrics_mgr.current_metrics["streak"] == 7
        assert metrics_mgr.current_metrics["avg_time"] == 3.0
        assert metrics_mgr.current_metrics["total_cards"] == 70  # 7 days * 10 cards

    def test_update_metrics_persists_to_file(self, tmp_path):
        """GIVEN progress data
        WHEN update_metrics is called
        THEN updated metrics should be saved to file
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [{"date": "2026-01-10", "steps": 8, "time": 3.5, "cards": 12}]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        metrics_mgr.update_metrics(progress_mgr.load_progress())

        # Verify file was created and contains correct data
        assert metrics_file.exists()
        saved_data = json.loads(metrics_file.read_text())
        assert saved_data["streak"] == 1
        assert saved_data["avg_time"] == 3.5
        assert saved_data["total_cards"] == 12

    def test_update_metrics_overwrites_old_values(self, tmp_path):
        """GIVEN existing outdated metrics
        WHEN update_metrics is called with new progress
        THEN old metrics should be replaced with fresh calculations
        """
        progress_file = tmp_path / "progress.json"
        metrics_file = tmp_path / "metrics.json"

        # Old metrics
        old_metrics = {"streak": 5, "avg_time": 2.0, "total_cards": 50}
        metrics_file.write_text(json.dumps(old_metrics))

        # New progress data
        today = date.today()
        progress_data = []
        for i in range(10):  # 10 consecutive days
            day = today - timedelta(days=9 - i)
            progress_data.append(
                {"date": day.strftime("%Y-%m-%d"), "steps": 7, "time": 4.0, "cards": 15}
            )

        progress_file.write_text(json.dumps(progress_data))

        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        metrics_mgr.update_metrics(progress_mgr.load_progress())

        # Verify new values
        assert metrics_mgr.current_metrics["streak"] == 10
        assert metrics_mgr.current_metrics["avg_time"] == 4.0
        assert metrics_mgr.current_metrics["total_cards"] == 150  # 10 * 15

        # Verify old values are gone
        assert metrics_mgr.current_metrics != old_metrics


class TestGetMetricsSummary:
    """Test getting formatted metrics summary for display."""

    def test_get_metrics_summary_returns_dict(self, tmp_path):
        """GIVEN calculated metrics
        WHEN get_metrics_summary is called
        THEN it should return a dict with all metrics
        """
        metrics_file = tmp_path / "metrics.json"
        manager = MetricsManager(metrics_file)

        manager.current_metrics = {"streak": 15, "avg_time": 3.5, "total_cards": 120}

        summary = manager.get_metrics_summary()

        assert isinstance(summary, dict)
        assert "streak" in summary
        assert "avg_time" in summary
        assert "total_cards" in summary

    def test_get_metrics_summary_includes_formatted_time(self, tmp_path):
        """GIVEN average time in hours (float)
        WHEN get_metrics_summary is called
        THEN it should include human-readable time format
        """
        metrics_file = tmp_path / "metrics.json"
        manager = MetricsManager(metrics_file)

        manager.current_metrics = {
            "streak": 10,
            "avg_time": 3.75,  # 3 hours 45 minutes
            "total_cards": 100,
        }

        summary = manager.get_metrics_summary()

        # Should have formatted time like "3h 45min"
        assert "avg_time_formatted" in summary or "time_formatted" in summary


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_metrics_with_zero_steps_days(self, tmp_path):
        """GIVEN progress entries with 0 steps (incomplete days)
        WHEN metrics are calculated
        THEN they should handle gracefully
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [{"date": "2026-01-10", "steps": 0, "time": 0.5, "cards": 2}]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        metrics_mgr.update_metrics(progress_mgr.load_progress())

        # Should not crash, should handle partial days
        assert isinstance(metrics_mgr.current_metrics["avg_time"], float)
        assert isinstance(metrics_mgr.current_metrics["total_cards"], int)

    def test_metrics_with_future_dates(self, tmp_path):
        """GIVEN progress with future dates (data integrity issue)
        WHEN metrics are calculated
        THEN it should handle without crashing
        """
        progress_file = tmp_path / "progress.json"
        future = date.today() + timedelta(days=5)
        progress_data = [
            {"date": future.strftime("%Y-%m-%d"), "steps": 8, "time": 3.0, "cards": 10}
        ]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        # Should not crash even with future dates
        metrics_mgr.update_metrics(progress_mgr.load_progress())
        assert isinstance(metrics_mgr.current_metrics, dict)

    def test_metrics_with_negative_values(self, tmp_path):
        """GIVEN progress with negative values (corrupted data)
        WHEN metrics are calculated
        THEN it should handle gracefully or sanitize
        """
        progress_file = tmp_path / "progress.json"
        progress_data = [
            {"date": "2026-01-10", "steps": -5, "time": -2.0, "cards": -10}
        ]
        progress_file.write_text(json.dumps(progress_data))

        metrics_file = tmp_path / "metrics.json"
        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        # Should handle without crashing (may clamp to 0 or skip)
        metrics_mgr.update_metrics(progress_mgr.load_progress())
        assert isinstance(metrics_mgr.current_metrics, dict)

    def test_concurrent_metrics_updates(self, tmp_path):
        """GIVEN multiple rapid update_metrics calls
        WHEN executed in sequence
        THEN final metrics should be consistent with last update
        """
        progress_file = tmp_path / "progress.json"
        metrics_file = tmp_path / "metrics.json"

        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        # Simulate rapid updates
        for i in range(3):
            progress_data = [
                {"date": f"2026-01-{10+i}", "steps": 8, "time": 3.0, "cards": 10 + i}
            ]
            progress_file.write_text(json.dumps(progress_data))
            progress_mgr = ProgressManager(progress_file)  # Reload
            metrics_mgr.update_metrics(progress_mgr.load_progress())

        # Last update should win
        assert metrics_mgr.current_metrics["total_cards"] == 12  # 10 + 2


class TestIntegrationWithProgressManager:
    """Integration tests between MetricsManager and ProgressManager."""

    def test_metrics_update_after_progress_save(self, tmp_path):
        """GIVEN a ProgressManager saving new daily progress
        WHEN MetricsManager updates from that progress
        THEN metrics should reflect the new entry
        """
        progress_file = tmp_path / "progress.json"
        metrics_file = tmp_path / "metrics.json"

        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        # Save initial progress
        today = date.today().strftime("%Y-%m-%d")
        progress_mgr.save_daily_progress(
            {"date": today, "steps": 8, "time": 3.5, "cards": 12}
        )

        # Update metrics
        metrics_mgr.update_metrics(progress_mgr.load_progress())

        assert metrics_mgr.current_metrics["total_cards"] == 12
        assert metrics_mgr.current_metrics["streak"] == 1

    def test_full_workflow_metrics_lifecycle(self, tmp_path):
        """GIVEN a complete workflow simulation
        WHEN user logs progress over multiple days
        THEN metrics should accurately track progression

        This simulates the US-002 Review Metrics use case
        """
        progress_file = tmp_path / "progress.json"
        metrics_file = tmp_path / "metrics.json"

        progress_mgr = ProgressManager(progress_file)
        metrics_mgr = MetricsManager(metrics_file)

        # Simulate 1 week of activity
        today = date.today()
        for i in range(7):
            day = today - timedelta(days=6 - i)
            progress_mgr.save_daily_progress(
                {
                    "date": day.strftime("%Y-%m-%d"),
                    "steps": 7 + (i % 2),  # Varying steps
                    "time": 2.5 + (i * 0.5),  # Increasing time
                    "cards": 8 + i,  # Increasing cards
                }
            )

        # Update metrics after week
        metrics_mgr.update_metrics(progress_mgr.load_progress())

        # Verify comprehensive metrics
        assert metrics_mgr.current_metrics["streak"] == 7
        assert metrics_mgr.current_metrics["avg_time"] > 0
        assert metrics_mgr.current_metrics["total_cards"] > 50

        # Verify persistence
        saved_metrics = json.loads(metrics_file.read_text())
        assert saved_metrics == metrics_mgr.current_metrics


class TestErrorHandling:
    """Test error handling and edge cases for robustness."""

    def test_save_metrics_with_readonly_file(self, tmp_path):
        """GIVEN a read-only file path
        WHEN save_metrics is called
        THEN it should raise IOError with descriptive message
        """
        metrics_file = tmp_path / "readonly.json"
        metrics_file.write_text('{"streak": 0}')
        metrics_file.chmod(0o444)  # Read-only

        manager = MetricsManager(metrics_file)
        manager.current_metrics = {"streak": 10, "avg_time": 5.0, "total_cards": 100}

        with pytest.raises(IOError, match="Error writing metrics"):
            manager.save_metrics()

        # Cleanup
        metrics_file.chmod(0o644)

    def test_load_metrics_with_invalid_permission(self, tmp_path):
        """GIVEN a file with no read permission
        WHEN load_metrics is called
        THEN it should return default metrics (graceful degradation)
        """
        metrics_file = tmp_path / "noperm.json"
        metrics_file.write_text('{"streak": 99}')
        metrics_file.chmod(0o000)  # No permissions

        manager = MetricsManager(metrics_file)
        loaded = manager.load_metrics()

        # Should return defaults when cannot read
        assert loaded == {"streak": 0, "avg_time": 0.0, "total_cards": 0}

        # Cleanup
        metrics_file.chmod(0o644)

    def test_get_average_time_with_empty_data_explicit(self, tmp_path):
        """GIVEN explicitly empty progress data (edge case validation)
        WHEN get_average_time is called
        THEN it should return 0.0 without division error
        """
        metrics_file = tmp_path / "metrics.json"
        manager = MetricsManager(metrics_file)

        # Explicitly test the count == 0 branch
        avg = manager.get_average_time([])

        assert avg == 0.0
        assert isinstance(avg, float)
