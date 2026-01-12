"""Tests for the Reflection step."""

from src.lms.steps.reflection import reflection_step


def test_reflection_creates_template(tmp_path):
    ok = reflection_step(storage_path=tmp_path, target_date="2026-01-12")
    assert ok is True
    note = tmp_path / "reflections" / "2026-01-12.md"
    assert note.exists()
    content = note.read_text()
    assert "# Reflection - 2026-01-12" in content
    assert "## Mood" in content
    assert "## Wins" in content


def test_reflection_is_idempotent(tmp_path):
    note = tmp_path / "reflections" / "2026-01-12.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("existing")
    ok = reflection_step(storage_path=tmp_path, target_date="2026-01-12")
    assert ok is True
    assert note.read_text() == "existing"
