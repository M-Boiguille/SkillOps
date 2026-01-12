"""Tests for the Read step."""

from datetime import datetime, timedelta
from pathlib import Path

from src.lms.steps.read import read_step, save_read_progress


def test_read_step_records_recent_notes(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    # Create three markdown files with staggered mtimes
    files = []
    base_time = datetime.now()
    for i in range(3):
        f = vault / f"note{i}.md"
        f.write_text(f"Note {i}")
        ts = base_time - timedelta(minutes=i)
        Path(f).touch(ts.timestamp())
        files.append(f)

    storage = tmp_path / "storage"
    ok = read_step(vault_path=vault, storage_path=storage)
    assert ok is True

    progress_file = storage / "read_progress.json"
    assert progress_file.exists()
    data = progress_file.read_text()
    assert "note0.md" in data
    assert "note1.md" in data
    assert "note2.md" in data


def test_read_step_missing_vault_returns_false(tmp_path):
    missing = tmp_path / "missing"
    storage = tmp_path / "storage"
    ok = read_step(vault_path=missing, storage_path=storage)
    assert ok is False


def test_save_read_progress_writes_json(tmp_path):
    notes = [tmp_path / "a.md", tmp_path / "b.md"]
    save_read_progress(tmp_path, notes)
    progress_file = tmp_path / "read_progress.json"
    assert progress_file.exists()
    content = progress_file.read_text()
    assert "a.md" in content
    assert "b.md" in content
