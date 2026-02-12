"""Tests for the quiz step using local SQLite cards."""

from datetime import datetime, timedelta
from pathlib import Path

from src.lms.database import get_connection, init_db
from src.lms.steps.anki import get_due_counts_by_topic, anki_step


def _seed_cards(storage_path: Path) -> None:
    init_db(storage_path=storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.executemany(
        """
        INSERT INTO quiz_cards (topic, question, answer, last_reviewed)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("Docker", "Q1", "A1", None),
            ("Docker", "Q2", "A2", yesterday),
            ("K8s", "Q3", "A3", today),
        ],
    )
    conn.commit()
    conn.close()


def test_get_due_counts_by_topic(tmp_path):
    storage_path = tmp_path
    _seed_cards(storage_path)

    counts = get_due_counts_by_topic(storage_path=storage_path)

    assert counts["Docker"] == 2
    assert "K8s" not in counts


def test_anki_step_empty(tmp_path, capsys):
    storage_path = tmp_path
    init_db(storage_path=storage_path)

    anki_step(storage_path=storage_path)

    captured = capsys.readouterr()
    assert "Aucune carte" in captured.out
