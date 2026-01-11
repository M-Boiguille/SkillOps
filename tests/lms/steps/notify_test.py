from unittest.mock import MagicMock, patch

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
@patch("src.lms.steps.notify.calculate_metrics_from_progress")
@patch("src.lms.steps.notify.ProgressManager")
def test_notify_step_sends_message(mock_pm, mock_calc, mock_client, tmp_path):
    storage_dir = tmp_path
    progress = {
        "steps": {"step1": {"completed": True, "time_spent": 600}},
        "cards_created": 3,
    }

    mock_pm_instance = MagicMock()
    mock_pm_instance.load_progress.return_value = [progress]
    mock_pm_instance.get_today_date.return_value = "2026-01-11"
    mock_pm_instance.get_progress_by_date.return_value = progress
    mock_pm.return_value = mock_pm_instance

    mock_calc.return_value = {
        "steps_completed": 1,
        "total_time": 600,
        "cards_created": 3,
        "streak": 2,
    }

    mock_client_instance = MagicMock()
    mock_client_instance.send_message.return_value = True
    mock_client.from_env.return_value = mock_client_instance

    sent = notify_step(storage_path=storage_dir, respect_schedule=False)

    assert sent is True
    mock_client_instance.send_message.assert_called_once()


@patch("src.lms.steps.notify.TelegramClient")
@patch("src.lms.steps.notify.calculate_metrics_from_progress")
@patch("src.lms.steps.notify.ProgressManager")
def test_notify_step_skips_if_already_sent(mock_pm, mock_calc, mock_client, tmp_path):
    storage_dir = tmp_path
    marker = storage_dir / ".notify_sent"
    marker.write_text("2026-01-11")

    progress = {
        "steps": {"step1": {"completed": True, "time_spent": 600}},
        "cards_created": 3,
    }

    mock_pm_instance = MagicMock()
    mock_pm_instance.load_progress.return_value = [progress]
    mock_pm_instance.get_today_date.return_value = "2026-01-11"
    mock_pm_instance.get_progress_by_date.return_value = progress
    mock_pm.return_value = mock_pm_instance

    mock_calc.return_value = {
        "steps_completed": 1,
        "total_time": 600,
        "cards_created": 3,
        "streak": 2,
    }

    sent = notify_step(storage_path=storage_dir, respect_schedule=False)

    assert sent is True
    mock_client.from_env.assert_not_called()


@patch("src.lms.steps.notify.TelegramClient")
@patch("src.lms.steps.notify.ProgressManager")
def test_notify_step_no_progress(mock_pm, mock_client, tmp_path, capsys):
    mock_pm_instance = MagicMock()
    mock_pm_instance.load_progress.return_value = []
    mock_pm_instance.get_today_date.return_value = "2026-01-11"
    mock_pm_instance.get_progress_by_date.return_value = None
    mock_pm.return_value = mock_pm_instance

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
@patch("src.lms.steps.notify.calculate_metrics_from_progress")
@patch("src.lms.steps.notify.ProgressManager")
def test_notify_step_idempotent_within_day(mock_pm, mock_calc, mock_client, tmp_path):
    """Notification should only send once per calendar day."""
    storage_dir = tmp_path
    progress = {
        "steps": {"step1": {"completed": True, "time_spent": 600}},
        "cards_created": 3,
    }

    mock_pm_instance = MagicMock()
    mock_pm_instance.load_progress.return_value = [progress]
    mock_pm_instance.get_today_date.return_value = "2026-01-11"
    mock_pm_instance.get_progress_by_date.return_value = progress
    mock_pm.return_value = mock_pm_instance

    mock_calc.return_value = {
        "steps_completed": 1,
        "total_time": 600,
        "cards_created": 3,
        "streak": 2,
    }

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
