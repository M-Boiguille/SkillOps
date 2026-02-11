from unittest.mock import MagicMock, patch

from src.lms.database import get_connection, init_db
from src.lms.steps.notify import (
    format_daily_report,
    notify_step,
    should_send_now,
)


def test_should_send_now_matches(monkeypatch):
    fixed_now = MagicMock()
    fixed_now.strftime.return_value = "20:00"
    assert should_send_now("20:00", now=fixed_now) is True
    assert should_send_now("21:00", now=fixed_now) is False


@patch("src.lms.steps.notify.TelegramClient")
def test_notify_step_sends_message(mock_client, tmp_path, monkeypatch):
    storage_dir = tmp_path
    monkeypatch.setattr("src.lms.steps.notify.get_logical_date", lambda: "2026-01-11")

    init_db(storage_dir)
    conn = get_connection(storage_dir)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (date) VALUES (?)", ("2026-01-11",))
    cursor.execute("SELECT id FROM sessions WHERE date = ?", ("2026-01-11",))
    session_id = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO step_completions (session_id, step_number) VALUES (?, ?)",
        (session_id, 1),
    )
    cursor.execute(
        "INSERT INTO formation_logs (session_id, goals, recall, "
        "duration_minutes) VALUES (?, ?, ?, ?)",
        (session_id, "[]", "", 10),
    )
    cursor.execute(
        "INSERT INTO card_creations (session_id, count, source) VALUES (?, ?, ?)",
        (session_id, 3, "test"),
    )
    conn.commit()
    conn.close()

    mock_client_instance = MagicMock()
    mock_client_instance.send_message.return_value = True
    mock_client.from_env.return_value = mock_client_instance

    sent = notify_step(storage_path=storage_dir, respect_schedule=False)

    assert sent is True
    mock_client_instance.send_message.assert_called_once()


@patch("src.lms.steps.notify.TelegramClient")
def test_notify_step_skips_if_already_sent(mock_client, tmp_path, monkeypatch):
    storage_dir = tmp_path
    marker = storage_dir / ".notify_sent"
    marker.write_text("2026-01-11")

    monkeypatch.setattr("src.lms.steps.notify.get_logical_date", lambda: "2026-01-11")

    sent = notify_step(storage_path=storage_dir, respect_schedule=False)

    assert sent is True
    mock_client.from_env.assert_not_called()


@patch("src.lms.steps.notify.TelegramClient")
def test_notify_step_no_progress(mock_client, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr("src.lms.steps.notify.get_logical_date", lambda: "2026-01-11")

    sent = notify_step(storage_path=tmp_path, respect_schedule=False)

    assert sent is False
    mock_client.from_env.assert_not_called()
    captured = capsys.readouterr().out
    assert "No data for today" in captured


def test_format_daily_report_includes_alerts():
    metrics = {
        "steps_completed": 2,
        "total_time": 1200,
        "cards_created": 1,
        "streak": 1,
    }
    report = format_daily_report("2026-01-11", metrics, {})
    assert "Day incomplete" in report
    assert "Low coding time" in report


@patch("src.lms.steps.notify.TelegramClient")
def test_notify_step_idempotent_within_day(mock_client, tmp_path, monkeypatch):
    """Notification should only send once per calendar day."""
    storage_dir = tmp_path
    monkeypatch.setattr("src.lms.steps.notify.get_logical_date", lambda: "2026-01-11")

    init_db(storage_dir)
    conn = get_connection(storage_dir)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (date) VALUES (?)", ("2026-01-11",))
    cursor.execute("SELECT id FROM sessions WHERE date = ?", ("2026-01-11",))
    session_id = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO step_completions (session_id, step_number) VALUES (?, ?)",
        (session_id, 1),
    )
    cursor.execute(
        "INSERT INTO formation_logs (session_id, goals, recall, "
        "duration_minutes) VALUES (?, ?, ?, ?)",
        (session_id, "[]", "", 10),
    )
    cursor.execute(
        "INSERT INTO card_creations (session_id, count, source) VALUES (?, ?, ?)",
        (session_id, 3, "test"),
    )
    conn.commit()
    conn.close()

    mock_client_instance = MagicMock()
    mock_client_instance.send_message.return_value = True
    mock_client.from_env.return_value = mock_client_instance

    # First call should send
    sent1 = notify_step(storage_path=storage_dir, respect_schedule=False)
    assert sent1 is True
    assert mock_client_instance.send_message.call_count == 1

    # Reset mock
    mock_client_instance.reset_mock()

    # Second call same day should skip
    sent2 = notify_step(storage_path=storage_dir, respect_schedule=False)
    assert sent2 is True
    mock_client_instance.send_message.assert_not_called()
