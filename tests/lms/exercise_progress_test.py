"""Tests for exercise progress tracking in ProgressManager."""

import pytest
from datetime import datetime

from lms.persistence import ProgressManager


def test_add_completed_exercise_to_new_date(tmp_path):
    """
    Given: An empty progress file
    When: Adding a completed exercise for a date
    Then: The exercise is saved with default progress values
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    result = pm.add_completed_exercise("2026-01-11", "ex001")
    
    assert result is True
    assert progress_file.exists()
    
    # Verify the entry was created
    loaded = pm.load_progress()
    assert len(loaded) == 1
    assert loaded[0]["date"] == "2026-01-11"
    assert loaded[0]["exercises_done"] == ["ex001"]
    assert loaded[0]["steps"] == 0
    assert loaded[0]["time"] == 0
    assert loaded[0]["cards"] == 0


def test_add_completed_exercise_to_existing_date(tmp_path):
    """
    Given: A progress file with existing entry for a date
    When: Adding a completed exercise to that date
    Then: The exercise is added to the existing exercises_done list
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    # Create initial progress entry
    initial_progress = {
        "date": "2026-01-11",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    pm.save_daily_progress(initial_progress)
    
    # Add exercise to existing date
    result = pm.add_completed_exercise("2026-01-11", "ex001")
    
    assert result is True
    
    # Verify exercise was added and other fields preserved
    loaded = pm.load_progress()
    assert len(loaded) == 1
    assert loaded[0]["date"] == "2026-01-11"
    assert loaded[0]["exercises_done"] == ["ex001"]
    assert loaded[0]["steps"] == 5
    assert loaded[0]["time"] == 120
    assert loaded[0]["cards"] == 10


def test_add_multiple_exercises_to_same_date(tmp_path):
    """
    Given: A progress file
    When: Adding multiple exercises to the same date
    Then: All exercises are stored in the exercises_done list
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    pm.add_completed_exercise("2026-01-11", "ex001")
    pm.add_completed_exercise("2026-01-11", "ex002")
    pm.add_completed_exercise("2026-01-11", "ex003")
    
    exercises = pm.get_completed_exercises("2026-01-11")
    
    assert len(exercises) == 3
    assert "ex001" in exercises
    assert "ex002" in exercises
    assert "ex003" in exercises


def test_add_duplicate_exercise_to_same_date(tmp_path):
    """
    Given: A progress file with an exercise already completed
    When: Adding the same exercise ID again to the same date
    Then: The exercise is not duplicated in the list
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    pm.add_completed_exercise("2026-01-11", "ex001")
    pm.add_completed_exercise("2026-01-11", "ex001")
    
    exercises = pm.get_completed_exercises("2026-01-11")
    
    assert len(exercises) == 1
    assert exercises[0] == "ex001"


def test_get_completed_exercises_empty_list_for_nonexistent_date(tmp_path):
    """
    Given: A progress file without data for a specific date
    When: Getting completed exercises for that date
    Then: An empty list is returned
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    exercises = pm.get_completed_exercises("2026-01-11")
    
    assert exercises == []


def test_get_completed_exercises_returns_copy(tmp_path):
    """
    Given: A progress file with completed exercises
    When: Getting completed exercises list
    Then: A copy is returned (not reference to internal list)
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    pm.add_completed_exercise("2026-01-11", "ex001")
    
    exercises1 = pm.get_completed_exercises("2026-01-11")
    exercises2 = pm.get_completed_exercises("2026-01-11")
    
    # Modify first list
    exercises1.append("ex999")
    
    # Second list should be unaffected
    assert "ex999" not in exercises2
    assert len(exercises2) == 1


def test_is_exercise_completed_returns_true_when_completed(tmp_path):
    """
    Given: A progress file with a completed exercise
    When: Checking if that exercise is completed
    Then: Returns True
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    pm.add_completed_exercise("2026-01-11", "ex001")
    
    result = pm.is_exercise_completed("2026-01-11", "ex001")
    
    assert result is True


def test_is_exercise_completed_returns_false_when_not_completed(tmp_path):
    """
    Given: A progress file without a specific exercise
    When: Checking if that exercise is completed
    Then: Returns False
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    pm.add_completed_exercise("2026-01-11", "ex001")
    
    result = pm.is_exercise_completed("2026-01-11", "ex002")
    
    assert result is False


def test_is_exercise_completed_returns_false_for_nonexistent_date(tmp_path):
    """
    Given: A progress file without data for a specific date
    When: Checking if an exercise is completed on that date
    Then: Returns False
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    result = pm.is_exercise_completed("2026-01-11", "ex001")
    
    assert result is False


def test_exercises_done_field_is_optional_in_existing_entries(tmp_path):
    """
    Given: Progress entries without exercises_done field (legacy format)
    When: Loading and accessing completed exercises
    Then: System handles missing field gracefully
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    # Create legacy format entry without exercises_done
    legacy_progress = {
        "date": "2026-01-10",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    pm.save_daily_progress(legacy_progress)
    
    # Should return empty list for missing field
    exercises = pm.get_completed_exercises("2026-01-10")
    assert exercises == []
    
    # Should return False for any exercise
    assert pm.is_exercise_completed("2026-01-10", "ex001") is False


def test_add_exercise_creates_parent_directories(tmp_path):
    """
    Given: A nested path that doesn't exist
    When: Adding a completed exercise
    Then: Parent directories are created automatically
    """
    nested_path = tmp_path / "nested" / "path" / "progress.json"
    pm = ProgressManager(nested_path)
    
    result = pm.add_completed_exercise("2026-01-11", "ex001")
    
    assert result is True
    assert nested_path.exists()
    assert nested_path.parent.exists()


def test_add_exercise_handles_io_error(tmp_path):
    """
    Given: A progress file with write permissions denied
    When: Adding a completed exercise
    Then: IOError is raised with descriptive message
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    # Create file and make it read-only
    pm.add_completed_exercise("2026-01-11", "ex001")
    progress_file.chmod(0o444)
    
    with pytest.raises(IOError, match="Error writing progress"):
        pm.add_completed_exercise("2026-01-11", "ex002")
    
    # Cleanup
    progress_file.chmod(0o644)


def test_exercises_persist_across_multiple_operations(tmp_path):
    """
    Given: A progress file
    When: Adding exercises, saving other progress, and loading again
    Then: Exercise data persists correctly across operations
    """
    progress_file = tmp_path / "progress.json"
    pm1 = ProgressManager(progress_file)
    
    # Add some exercises
    pm1.add_completed_exercise("2026-01-11", "ex001")
    pm1.add_completed_exercise("2026-01-11", "ex002")
    
    # Create new instance and verify data persists
    pm2 = ProgressManager(progress_file)
    exercises = pm2.get_completed_exercises("2026-01-11")
    
    assert len(exercises) == 2
    assert "ex001" in exercises
    assert "ex002" in exercises


def test_is_valid_progress_accepts_entries_with_exercises_done(tmp_path):
    """
    Given: A progress entry with exercises_done field
    When: Validating the entry
    Then: Entry is considered valid
    """
    pm = ProgressManager()
    
    progress_with_exercises = {
        "date": "2026-01-11",
        "steps": 5,
        "time": 120,
        "cards": 10,
        "exercises_done": ["ex001", "ex002"]
    }
    
    assert pm.is_valid_progress(progress_with_exercises) is True


def test_is_valid_progress_accepts_entries_without_exercises_done(tmp_path):
    """
    Given: A progress entry without exercises_done field (legacy format)
    When: Validating the entry
    Then: Entry is considered valid (backward compatibility)
    """
    pm = ProgressManager()
    
    legacy_progress = {
        "date": "2026-01-11",
        "steps": 5,
        "time": 120,
        "cards": 10
    }
    
    assert pm.is_valid_progress(legacy_progress) is True


def test_add_exercises_to_different_dates(tmp_path):
    """
    Given: A progress file
    When: Adding exercises to multiple different dates
    Then: Each date maintains its own separate exercises_done list
    """
    progress_file = tmp_path / "progress.json"
    pm = ProgressManager(progress_file)
    
    pm.add_completed_exercise("2026-01-10", "ex001")
    pm.add_completed_exercise("2026-01-10", "ex002")
    pm.add_completed_exercise("2026-01-11", "ex003")
    pm.add_completed_exercise("2026-01-11", "ex004")
    
    exercises_jan10 = pm.get_completed_exercises("2026-01-10")
    exercises_jan11 = pm.get_completed_exercises("2026-01-11")
    
    assert len(exercises_jan10) == 2
    assert "ex001" in exercises_jan10
    assert "ex002" in exercises_jan10
    
    assert len(exercises_jan11) == 2
    assert "ex003" in exercises_jan11
    assert "ex004" in exercises_jan11
