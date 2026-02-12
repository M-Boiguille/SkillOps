"""Tests for Phase 3 passive tracking (git hooks + WakaTime)."""

from src.lms.database import init_db, get_connection
from src.lms.git_hooks import (
    record_commit_to_db,
    get_today_commits,
    calculate_session_metrics,
    install_post_commit_hook,
)
from src.lms.passive_tracking import (
    collect_daily_tracking_data,
    merge_session_data,
    get_tracking_summary,
    _estimate_activity_level,
)


class TestGitHooks:
    """Tests for git hook integration."""

    def test_install_post_commit_hook_no_git_repo(self, tmp_path, monkeypatch):
        """Test hook installation fails gracefully in non-git directory."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        # Directory has no .git folder
        assert install_post_commit_hook(tmp_path) is False

    def test_record_commit_to_db(self, tmp_path, monkeypatch):
        """Test recording a commit to SQLite."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        result = record_commit_to_db(
            commit_hash="abc123",
            commit_time="2026-02-12T10:30:00Z",
            commit_msg="Add feature X",
            files_changed=3,
            lines_added=45,
            lines_deleted=12,
            storage_path=tmp_path,
        )

        assert result is True

        # Verify data was stored
        commits = get_today_commits(storage_path=tmp_path)
        assert len(commits) == 1
        assert commits[0]["hash"] == "abc123"
        assert commits[0]["files_changed"] == 3

    def test_get_today_commits(self, tmp_path, monkeypatch):
        """Test retrieving commits for today."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        # Record multiple commits
        for i in range(3):
            record_commit_to_db(
                commit_hash=f"hash{i}",
                commit_time="2026-02-12T10:30:00Z",
                commit_msg=f"Commit {i}",
                files_changed=i + 1,
                lines_added=10 * (i + 1),
                lines_deleted=5 * (i + 1),
                storage_path=tmp_path,
            )

        commits = get_today_commits(storage_path=tmp_path)
        assert len(commits) == 3

    def test_calculate_session_metrics_no_commits(self, tmp_path, monkeypatch):
        """Test metrics calculation with no commits."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        metrics = calculate_session_metrics(storage_path=tmp_path)

        assert metrics["commits_count"] == 0
        assert metrics["files_changed"] == 0
        assert metrics["total_changes"] == 0

    def test_calculate_session_metrics_with_commits(self, tmp_path, monkeypatch):
        """Test metrics calculation with commits."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        record_commit_to_db(
            commit_hash="hash1",
            commit_time="2026-02-12T10:30:00Z",
            commit_msg="First commit",
            files_changed=3,
            lines_added=50,
            lines_deleted=10,
            storage_path=tmp_path,
        )

        record_commit_to_db(
            commit_hash="hash2",
            commit_time="2026-02-12T11:45:00Z",
            commit_msg="Second commit",
            files_changed=2,
            lines_added=30,
            lines_deleted=5,
            storage_path=tmp_path,
        )

        metrics = calculate_session_metrics(storage_path=tmp_path)

        assert metrics["commits_count"] == 2
        assert metrics["files_changed"] == 5
        assert metrics["lines_added"] == 80
        assert metrics["lines_deleted"] == 15
        assert metrics["total_changes"] == 95


class TestPassiveTracking:
    """Tests for passive tracking integration."""

    def test_estimate_activity_level_inactive(self):
        """Test activity level estimation for inactive day."""
        level = _estimate_activity_level(0, 0)
        assert level == "inactive"

    def test_estimate_activity_level_low(self):
        """Test activity level estimation for low activity."""
        level = _estimate_activity_level(1000, 1)  # < 30 min, < 3 commits
        assert level == "low"

    def test_estimate_activity_level_moderate(self):
        """Test activity level estimation for moderate activity."""
        level = _estimate_activity_level(2700, 5)  # 45 min, 5 commits
        assert level == "moderate"

    def test_estimate_activity_level_high(self):
        """Test activity level estimation for high activity."""
        level = _estimate_activity_level(5400, 15)  # 1.5 hours, 15 commits
        assert level == "high"

    def test_merge_session_data(self):
        """Test merging WakaTime and git data."""
        wakatime_data = {
            "total_seconds": 3600,
            "languages": [{"name": "Python", "percent": 80}],
            "projects": [{"name": "SkillOps", "percent": 100}],
            "editors": [{"name": "VSCode", "percent": 100}],
        }

        git_data = {
            "commits_count": 5,
            "files_changed": 10,
            "lines_added": 100,
            "lines_deleted": 20,
            "total_changes": 120,
        }

        merged = merge_session_data(wakatime_data, git_data)

        assert merged["wakatime"]["total_seconds"] == 3600
        assert merged["git"]["commits"] == 5
        assert merged["summary"]["activity_level"] == "high"

    def test_merge_session_data_partial(self):
        """Test merging with only some data available."""
        git_data = {
            "commits_count": 2,
            "files_changed": 3,
            "lines_added": 25,
            "lines_deleted": 5,
            "total_changes": 30,
        }

        merged = merge_session_data(None, git_data)

        assert merged["wakatime"]["total_seconds"] == 0
        assert merged["git"]["commits"] == 2

    def test_collect_daily_tracking_data(self, tmp_path, monkeypatch):
        """Test collecting all tracking data for the day."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        # Add some commits
        record_commit_to_db(
            commit_hash="test_hash",
            commit_time="2026-02-12T10:30:00Z",
            commit_msg="Test commit",
            files_changed=2,
            lines_added=30,
            lines_deleted=5,
            storage_path=tmp_path,
        )

        tracking_data = collect_daily_tracking_data(storage_path=tmp_path)

        assert "wakatime" in tracking_data
        assert "git" in tracking_data
        assert "summary" in tracking_data
        assert tracking_data["git"]["commits"] == 1

    def test_get_tracking_summary(self, tmp_path, monkeypatch):
        """Test retrieving stored tracking summary."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        monkeypatch.setattr("src.lms.database.get_logical_date", lambda: "2026-02-12")

        init_db(tmp_path)

        # Collect data to store summary
        record_commit_to_db(
            commit_hash="test_hash",
            commit_time="2026-02-12T10:30:00Z",
            commit_msg="Test commit",
            files_changed=2,
            lines_added=30,
            lines_deleted=5,
            storage_path=tmp_path,
        )

        collect_daily_tracking_data(storage_path=tmp_path)

        # Retrieve summary
        summary = get_tracking_summary(date_str="2026-02-12", storage_path=tmp_path)

        assert summary is not None
        assert summary["git_commits"] == 1
        assert summary["activity_level"] in ["low", "inactive"]


class TestSchemaVersion:
    """Tests for schema migration to version 7."""

    def test_schema_version_7_tables_created(self, tmp_path, monkeypatch):
        """Test that schema v7 creates tracking tables."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        init_db(tmp_path)

        conn = get_connection(tmp_path)
        cursor = conn.cursor()

        # Check code_sessions table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='code_sessions'"
        )
        assert cursor.fetchone() is not None

        # Check tracking_summary table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tracking_summary'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_schema_version_has_v7(self, tmp_path, monkeypatch):
        """Test that schema version reaches 7."""
        monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
        init_db(tmp_path)

        conn = get_connection(tmp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) FROM schema_version")
        version = cursor.fetchone()[0]
        conn.close()

        assert version >= 7
