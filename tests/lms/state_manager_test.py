import os
import pytest

from lms.persistence import StateManager


def test_load_state_creates_default_if_file_does_not_exist(tmp_path):
    state_file = tmp_path / "state.yaml"
    sm = StateManager(state_file)

    sm.load_state()

    assert sm.get_current_state() == {
        "session_id": None,
        "step_id": None,
        "timestamp": None,
    }


def test_save_state_creates_file(tmp_path):
    state_file = tmp_path / "state.yaml"
    sm = StateManager(state_file)

    sm.load_state()
    sm.save_state()

    assert state_file.exists()


def test_save_and_load_state_roundtrip(tmp_path):
    state_file = tmp_path / "state.yaml"
    sm = StateManager(state_file)

    state = {
        "session_id": "session_1",
        "step_id": "step_1",
        "timestamp": "2026-01-09T10:00:00Z",
    }

    sm.current_state = state
    sm.save_state()

    sm2 = StateManager(state_file)
    sm2.load_state()

    assert sm2.get_current_state() == state


def test_load_state_empty_yaml_returns_template(tmp_path):
    state_file = tmp_path / "state.yaml"
    state_file.write_text("")

    sm = StateManager(state_file)
    sm.load_state()

    assert sm.get_current_state() == {
        "session_id": None,
        "step_id": None,
        "timestamp": None,
    }


def test_save_state_does_nothing_if_state_is_none(tmp_path):
    state_file = tmp_path / "state.yaml"
    sm = StateManager(state_file)

    sm.save_state()

    assert not state_file.exists()


def test_permission_error_on_read(monkeypatch, tmp_path):
    """Test that PermissionError is raised when file exists but can't be read."""
    state_file = tmp_path / "state.yaml"
    # Create the file first so it exists
    state_file.write_text("session_id: test\nstep_id: 1\ntimestamp: 123\n")
    
    sm = StateManager(state_file)
    
    # Mock os.access to return False for read permission
    def mock_access(path, mode):
        if mode == os.R_OK:
            return False
        return True
    
    monkeypatch.setattr(os, "access", mock_access)
    
    with pytest.raises(PermissionError, match="Permission denied"):
        sm.load_state()


def test_permission_error_on_write(monkeypatch, tmp_path):
    """Test that PermissionError is raised when file exists but can't be written."""
    state_file = tmp_path / "state.yaml"
    # Create the file first so it exists
    state_file.write_text("session_id: test\nstep_id: 1\ntimestamp: 123\n")
    
    sm = StateManager(state_file)
    sm.load_state()
    
    # Mock os.access to return False for write permission
    def mock_access(path, mode):
        if mode == os.W_OK:
            return False
        return True
    
    monkeypatch.setattr(os, "access", mock_access)
    
    with pytest.raises(PermissionError, match="Permission denied"):
        sm.save_state()


def test_is_valid_state_with_valid_state():
    """Test is_valid_state returns True for valid state."""
    sm = StateManager()
    valid_state = {
        "session_id": "test_session",
        "step_id": "step_1",
        "timestamp": "2026-01-09T10:00:00Z",
    }
    assert sm.is_valid_state(valid_state) is True


def test_is_valid_state_with_none():
    """Test is_valid_state returns False for None."""
    sm = StateManager()
    assert sm.is_valid_state(None) is False


def test_is_valid_state_with_missing_keys():
    """Test is_valid_state returns False when keys are missing."""
    sm = StateManager()
    invalid_state = {"session_id": "test_session", "step_id": "step_1"}
    assert sm.is_valid_state(invalid_state) is False


def test_is_valid_state_with_extra_keys():
    """Test is_valid_state returns True even with extra keys."""
    sm = StateManager()
    state_with_extra = {
        "session_id": "test_session",
        "step_id": "step_1",
        "timestamp": "2026-01-09T10:00:00Z",
        "extra_field": "some_value",
    }
    assert sm.is_valid_state(state_with_extra) is True


def test_load_state_with_invalid_yaml(tmp_path):
    """Test that load_state creates default state when YAML is invalid."""
    state_file = tmp_path / "state.yaml"
    state_file.write_text("invalid: yaml: content: [[[")
    
    sm = StateManager(state_file)
    
    with pytest.raises(IOError, match="Error loading state"):
        sm.load_state()


def test_save_state_creates_parent_directories(tmp_path):
    """Test that save_state creates parent directories if they don't exist."""
    nested_path = tmp_path / "nested" / "path" / "state.yaml"
    sm = StateManager(nested_path)
    
    sm.current_state = {
        "session_id": "test",
        "step_id": "1",
        "timestamp": "123",
    }
    sm.save_state()
    
    assert nested_path.exists()
    assert nested_path.parent.exists()


def test_template_independence(tmp_path):
    """Test that modifying current_state doesn't affect the template."""
    state_file = tmp_path / "state.yaml"
    sm = StateManager(state_file)
    sm.load_state()  # Creates a copy of template
    
    original_template = sm.template.copy()
    sm.current_state["session_id"] = "modified"
    
    # Template should remain unchanged
    assert sm.template == original_template
    assert sm.template["session_id"] is None


def test_get_current_state_returns_none_initially():
    """Test that get_current_state returns None before load_state is called."""
    sm = StateManager()
    assert sm.get_current_state() is None


def test_load_state_with_incomplete_state(tmp_path):
    """Test that incomplete state is replaced with template."""
    state_file = tmp_path / "state.yaml"
    state_file.write_text("session_id: test_session\nstep_id: step_1\n")  # Missing timestamp
    
    sm = StateManager(state_file)
    sm.load_state()
    
    assert sm.get_current_state() == {
        "session_id": None,
        "step_id": None,
        "timestamp": None,
    }

