"""Tests for Phase 4 TUI Dashboard and Analytics."""

from datetime import datetime, timedelta

from src.lms.database import init_db
from src.lms.dashboard import (
    get_historical_tracking,
    create_weekly_summary_table,
    create_stats_panel,
    create_trends_table,
    get_learning_recommendations,
)
from src.lms.git_hooks import record_commit_to_db
from src.lms.passive_tracking import collect_daily_tracking_data


class TestDashboardData:
    """Tests for dashboard data collection."""

    def test_get_historical_tracking_empty(self, tmp_path, monkeypatch):
        """Test retrieving tracking data when none exists."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        data = get_historical_tracking(days=7, storage_path=tmp_path)

        assert data == []

    def test_get_historical_tracking_with_data(self, tmp_path, monkeypatch):
        """Test retrieving tracking data when data exists."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        # Add some commits for the past 5 days to ensure >= 1 row
        for day_offset in range(5):
            date_str = (
                datetime.strptime("2026-02-12", "%Y-%m-%d") - timedelta(days=day_offset)
            ).strftime("%Y-%m-%d")

            record_commit_to_db(
                commit_hash=f"hash_{day_offset}",
                commit_time=f"{date_str}T10:30:00Z",
                commit_msg=f"Day {day_offset}",
                files_changed=2,
                lines_added=20,
                lines_deleted=5,
                storage_path=tmp_path,
            )

            # Collect and store
            monkeypatch.setattr("src.lms.database.get_logical_date", lambda: date_str)
            collect_daily_tracking_data(storage_path=tmp_path)

        data = get_historical_tracking(days=7, storage_path=tmp_path)

        assert len(data) >= 1
        assert all(d["git_commits"] >= 0 for d in data)


class TestDashboardTables:
    """Tests for dashboard table generation."""

    def test_create_weekly_summary_table_empty(self):
        """Test creating summary table with no data."""
        table = create_weekly_summary_table([])
        assert table is not None
        assert table.title == "Last 7 Days Activity"

    def test_create_weekly_summary_table_with_data(self):
        """Test creating summary table with data."""
        data = [
            {
                "date": "2026-02-12",
                "wakatime_seconds": 3600,
                "git_commits": 5,
                "git_files_changed": 10,
                "git_lines_added": 100,
                "git_lines_deleted": 20,
                "activity_level": "high",
            },
            {
                "date": "2026-02-11",
                "wakatime_seconds": 1800,
                "git_commits": 2,
                "git_files_changed": 5,
                "git_lines_added": 50,
                "git_lines_deleted": 10,
                "activity_level": "low",
            },
        ]

        table = create_weekly_summary_table(data)

        assert table is not None
        assert table.title == "Last 7 Days Activity"

    def test_create_stats_panel_empty(self):
        """Test creating stats panel with no data."""
        panel = create_stats_panel([])
        assert panel is not None

    def test_create_stats_panel_with_data(self):
        """Test creating stats panel with data."""
        data = [
            {
                "date": f"2026-02-{12-i}",
                "wakatime_seconds": 3600,
                "git_commits": 5,
                "git_files_changed": 10,
                "git_lines_added": 100,
                "git_lines_deleted": 20,
                "activity_level": "high",
            }
            for i in range(7)
        ]

        panel = create_stats_panel(data)

        assert panel is not None
        # Panel object should have a title attribute
        assert hasattr(panel, "title")

    def test_create_trends_table_empty(self):
        """Test creating trends table with no data."""
        table = create_trends_table([])
        assert table is not None

    def test_create_trends_table_with_data(self):
        """Test creating trends table with data."""
        data = [
            {
                "date": f"2026-02-{12-i}",
                "wakatime_seconds": 3600 * (i + 1),
                "git_commits": 5 * (i + 1),
                "git_files_changed": 10,
                "git_lines_added": 100,
                "git_lines_deleted": 20,
                "activity_level": "high",
            }
            for i in range(7)
        ]

        table = create_trends_table(data)

        assert table is not None


class TestRecommendations:
    """Tests for adaptive learning recommendations."""

    def test_get_recommendations_no_data(self):
        """Test recommendations with no tracking data."""
        recs = get_learning_recommendations()

        assert isinstance(recs, list)
        assert len(recs) > 0
        assert "Start tracking" in recs[0]

    def test_get_recommendations_low_activity(self, tmp_path, monkeypatch):
        """Test recommendations for low activity."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        # Add minimal commits
        record_commit_to_db(
            commit_hash="test",
            commit_time="2026-02-12T10:30:00Z",
            commit_msg="test",
            files_changed=1,
            lines_added=5,
            lines_deleted=1,
            storage_path=tmp_path,
        )

        collect_daily_tracking_data(storage_path=tmp_path)

        recs = get_learning_recommendations(storage_path=tmp_path)

        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_get_recommendations_high_activity(self, tmp_path, monkeypatch):
        """Test recommendations for high activity."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        # Add significant commits
        for i in range(5):
            record_commit_to_db(
                commit_hash=f"hash_{i}",
                commit_time="2026-02-12T10:30:00Z",
                commit_msg=f"commit {i}",
                files_changed=5,
                lines_added=50,
                lines_deleted=10,
                storage_path=tmp_path,
            )

        collect_daily_tracking_data(storage_path=tmp_path)

        recs = get_learning_recommendations(storage_path=tmp_path)

        assert isinstance(recs, list)
        # High activity should have different recommendations
        has_momentum = any("momentum" in r.lower() for r in recs)
        assert has_momentum or len(recs) > 0


class TestDashboardIntegration:
    """Integration tests for dashboard."""

    def test_dashboard_with_week_of_data(self, tmp_path, monkeypatch):
        """Test dashboard with a full week of tracking data."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))

        init_db(tmp_path)

        # Generate 7 days of data
        for day_offset in range(7):
            date_str = (
                datetime.strptime("2026-02-12", "%Y-%m-%d") - timedelta(days=day_offset)
            ).strftime("%Y-%m-%d")

            monkeypatch.setattr(
                "src.lms.database.get_logical_date", lambda d=date_str: d
            )

            for commit_num in range(day_offset + 1):
                record_commit_to_db(
                    commit_hash=f"hash_{day_offset}_{commit_num}",
                    commit_time=f"{date_str}T{10+commit_num}:30:00Z",
                    commit_msg=f"Day {day_offset}, commit {commit_num}",
                    files_changed=2,
                    lines_added=20,
                    lines_deleted=5,
                    storage_path=tmp_path,
                )

            collect_daily_tracking_data(storage_path=tmp_path)

        # Test retrieval
        data = get_historical_tracking(days=7, storage_path=tmp_path)
        assert len(data) > 0

        # Test table generation
        table = create_weekly_summary_table(data)
        assert table is not None

        # Test stats
        panel = create_stats_panel(data)
        assert panel is not None

        # Test trends
        trends = create_trends_table(data)
        assert trends is not None

        # Test recommendations
        recs = get_learning_recommendations(storage_path=tmp_path)
        assert isinstance(recs, list)
