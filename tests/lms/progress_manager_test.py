import pytest
from datetime import datetime, timedelta

from lms.persistence import ProgressManager


def test_load_progress_creates_empty_list_if_file_does_not_exist(tmp_path):
    """Test that load_progress returns empty list when file doesn't exist."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    result = pm.load_progress()
    
    assert result == []


def test_save_daily_progress_creates_file(tmp_path):
    """Test that save_daily_progress creates the JSON file."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    progress_data = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress_data)
    
    assert progress_file.exists()


def test_save_and_load_progress_roundtrip(tmp_path):
    """Test that saved progress can be loaded back correctly."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    progress_data = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress_data)
    
    loaded_progress = pm.load_progress()
    
    assert len(loaded_progress) == 1
    assert loaded_progress[0] == progress_data


def test_save_multiple_daily_progress_entries(tmp_path):
    """Test that multiple progress entries are saved as array."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    progress1 = {
        "date": "2026-01-09",
        "steps": 3,
        "time": 90,
        "cards": 8
    }
    progress2 = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress1)
    pm.save_daily_progress(progress2)
    
    loaded_progress = pm.load_progress()
    
    assert len(loaded_progress) == 2
    assert loaded_progress[0] == progress1
    assert loaded_progress[1] == progress2


def test_get_yesterday_progress_returns_correct_entry(tmp_path):
    """Test that get_yesterday_progress returns yesterday's data."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    progress_yesterday = {
        "date": yesterday,
        "steps": 3,
        "time": 90,
        "cards": 8
    }
    progress_today = {
        "date": today,
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress_yesterday)
    pm.save_daily_progress(progress_today)
    
    result = pm.get_yesterday_progress()
    
    assert result == progress_yesterday


def test_get_yesterday_progress_returns_none_if_not_found(tmp_path):
    """Test that get_yesterday_progress returns None when no yesterday data."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    progress_data = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress_data)
    
    result = pm.get_yesterday_progress()
    
    assert result is None


def test_load_progress_empty_json_returns_empty_list(tmp_path):
    """Test that empty JSON file returns empty list."""
    progress_file = tmp_path / "progress.json"
    progress_file.write_text("[]")
    
    pm = ProgressManager(progress_file)
    result = pm.load_progress()
    
    assert result == []


def test_load_progress_with_invalid_json(tmp_path):
    """Test that load_progress raises IOError for invalid JSON."""
    progress_file = tmp_path / "progress.json"
    progress_file.write_text("invalid json {[")
    
    pm = ProgressManager(progress_file)
    
    with pytest.raises(IOError, match="Error loading progress"):
        pm.load_progress()


def test_save_progress_creates_parent_directories(tmp_path):
    """Test that save_daily_progress creates parent directories."""
    nested_path = tmp_path / "nested" / "path" / "progress.json"
    pm = ProgressManager(nested_path)
    
    progress_data = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress_data)
    
    assert nested_path.exists()
    assert nested_path.parent.exists()


def test_permission_error_on_read(tmp_path):
    """Test that IOError wraps PermissionError when file can't be read."""
    progress_file = tmp_path / "progress.json"
    progress_file.write_text("[]")
    progress_file.chmod(0o000)
    
    pm = ProgressManager(progress_file)
    
    with pytest.raises(IOError, match="Error loading progress"):
        pm.load_progress()
    
    progress_file.chmod(0o644)


def test_permission_error_on_write(tmp_path):
    """Test that IOError wraps PermissionError when file can't be written."""
    progress_file = tmp_path / "progress.json"
    progress_file.write_text("[]")
    
    pm = ProgressManager(progress_file)
    pm.load_progress()
    
    progress_file.chmod(0o444)
    
    progress_data = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    with pytest.raises(IOError, match="Error writing progress"):
        pm.save_daily_progress(progress_data)
    
    progress_file.chmod(0o644)


def test_is_valid_progress_with_valid_data():
    """Test is_valid_progress returns True for valid progress entry."""
    pm = ProgressManager()
    
    valid_progress = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    assert pm.is_valid_progress(valid_progress) is True


def test_is_valid_progress_with_missing_keys():
    """Test is_valid_progress returns False for missing required keys."""
    pm = ProgressManager()
    
    invalid_progress = {
        "date": "2026-01-10",
        "steps": 5
        # Missing time, cards
    }
    
    assert pm.is_valid_progress(invalid_progress) is False


def test_is_valid_progress_with_none():
    """Test is_valid_progress returns False for None."""
    pm = ProgressManager()
    
    assert pm.is_valid_progress(None) is False


def test_is_valid_progress_with_extra_keys():
    """Test is_valid_progress returns True even with extra keys."""
    pm = ProgressManager()
    
    progress_with_extra = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10,
        "notes": "Great progress today"
    }
    
    assert pm.is_valid_progress(progress_with_extra) is True


def test_save_invalid_progress_does_nothing(tmp_path):
    """Test that saving invalid progress doesn't modify file."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    invalid_progress = {
        "date": "2026-01-10"
        # Missing required fields
    }
    
    pm.save_daily_progress(invalid_progress)
    
    # File should not be created or modified
    if progress_file.exists():
        loaded = pm.load_progress()
        assert len(loaded) == 0


def test_get_progress_by_date(tmp_path):
    """Test getting progress for a specific date."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    progress1 = {
        "date": "2026-01-08",
        "steps": 3,
        "time": 90,
        "cards": 8
    }
    progress2 = {
        "date": "2026-01-09",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress1)
    pm.save_daily_progress(progress2)
    
    result = pm.get_progress_by_date("2026-01-09")
    
    assert result == progress2


def test_get_progress_by_date_returns_none_if_not_found(tmp_path):
    """Test that get_progress_by_date returns None if date not found."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    progress_data = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress_data)
    
    result = pm.get_progress_by_date("2026-01-09")
    
    assert result is None


def test_load_progress_returns_new_instance_each_time(tmp_path):
    """Test that load_progress returns independent copies."""
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    progress_data = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    pm.save_daily_progress(progress_data)
    
    loaded1 = pm.load_progress()
    loaded2 = pm.load_progress()
    
    # Modify first loaded list
    loaded1[0]["steps"] = 999
    
    # Second loaded list should be unaffected
    assert loaded2[0]["steps"] == 5
