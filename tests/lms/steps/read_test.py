"""Tests for the Read step."""

import pytest

from datetime import datetime, timedelta
from pathlib import Path

from src.lms.database import get_connection, init_db
from src.lms.steps.read import read_step, save_read_progress

pytest.skip("Legacy read step removed", allow_module_level=True)


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

    conn = get_connection(storage)
    cursor = conn.cursor()
    cursor.execute("SELECT notes FROM read_sessions")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert "note0.md" in row[0]
    assert "note1.md" in row[0]
    assert "note2.md" in row[0]


def test_read_step_missing_vault_returns_false(tmp_path):
    missing = tmp_path / "missing"
    storage = tmp_path / "storage"
    ok = read_step(vault_path=missing, storage_path=storage)
    assert ok is False


def test_save_read_progress_writes_sqlite(tmp_path):
    init_db(tmp_path)
    notes = [tmp_path / "a.md", tmp_path / "b.md"]
    save_read_progress(tmp_path, notes)

    conn = get_connection(tmp_path)
    cursor = conn.cursor()
    cursor.execute("SELECT notes FROM read_sessions")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert "a.md" in row[0]
    assert "b.md" in row[0]
