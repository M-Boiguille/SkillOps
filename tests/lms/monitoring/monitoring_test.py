"""Tests for monitoring modules."""

from datetime import datetime
from datetime import timedelta
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from src.lms.monitoring.error_aggregator import ErrorAggregator
from src.lms.monitoring.metrics import MetricsCollector
from src.lms.monitoring.syslog_handler import setup_syslog_handler


class TestErrorAggregator:
    """Tests for error aggregation and deduplication."""

    def test_record_new_error(self, tmp_path):
        """Test recording a new error."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        error = ValueError("Test error")

        is_new = aggregator.record_error(error, step_id="create")

        assert is_new is True
        assert aggregator.get_error_count() == 1

    def test_deduplicate_same_error(self, tmp_path):
        """Test that same error within 24h is deduplicated."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        error = ValueError("Test error")

        # Record same error twice
        aggregator.record_error(error, step_id="create")
        is_new = aggregator.record_error(error, step_id="create")

        assert is_new is False
        assert aggregator.get_error_count() == 1

    def test_different_errors_not_deduplicated(self, tmp_path):
        """Test that different errors are tracked separately."""
        aggregator = ErrorAggregator(storage_path=tmp_path)

        aggregator.record_error(ValueError("Error 1"), step_id="create")
        aggregator.record_error(TypeError("Error 2"), step_id="create")

        assert aggregator.get_error_count() == 2

    def test_same_error_different_steps(self, tmp_path):
        """Test that same error in different steps is tracked separately."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        error = ValueError("Test error")

        aggregator.record_error(error, step_id="create")
        aggregator.record_error(error, step_id="share")

        assert aggregator.get_error_count() == 2

    def test_get_daily_summary(self, tmp_path):
        """Test retrieving daily error summary."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        aggregator.record_error(ValueError("Error 1"), step_id="create")
        aggregator.record_error(TypeError("Error 2"), step_id="share")

        summary = aggregator.get_daily_summary()

        assert len(summary) == 2
        assert all(isinstance(errors, list) for errors in summary.values())

    def test_get_summary_by_step(self, tmp_path):
        """Test retrieving error summary grouped by step."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        aggregator.record_error(ValueError("Error 1"), step_id="create")
        aggregator.record_error(ValueError("Error 2"), step_id="create")
        aggregator.record_error(TypeError("Error 3"), step_id="share")

        summary = aggregator.get_summary_by_step()

        assert "create" in summary
        assert "share" in summary
        assert summary["create"]["count"] == 2
        assert summary["share"]["count"] == 1

    def test_critical_errors_today(self, tmp_path):
        """Test detection of critical errors."""
        aggregator = ErrorAggregator(storage_path=tmp_path)

        assert aggregator.critical_errors_today() is False

        aggregator.record_error(ValueError("Test"), step_id="create")

        assert aggregator.critical_errors_today() is True

    def test_error_with_context(self, tmp_path):
        """Test recording error with additional context."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        error = ValueError("API Error")
        context = {"api": "github", "status_code": 401}

        aggregator.record_error(error, step_id="share", context=context)

        summary = aggregator.get_daily_summary()
        assert len(summary) == 1

    def test_error_with_retry_count(self, tmp_path):
        """Test recording error with retry information."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        error = ConnectionError("Network timeout")

        aggregator.record_error(error, step_id="notify", retry_count=3)

        summary = aggregator.get_daily_summary()
        assert len(summary) == 1

    def test_clear_errors(self, tmp_path):
        """Test clearing all recorded errors."""
        aggregator = ErrorAggregator(storage_path=tmp_path)
        aggregator.record_error(ValueError("Test"), step_id="create")

        assert aggregator.get_error_count() == 1

        aggregator.clear_errors()

        assert aggregator.get_error_count() == 0

    def test_prune_old_errors(self, tmp_path):
        """Test that errors older than 24h are pruned."""
        aggregator = ErrorAggregator(storage_path=tmp_path)

        # Record an error
        aggregator.record_error(ValueError("Old error"), step_id="create")

        # Manually modify timestamp to be 25 hours old
        errors = aggregator._load_errors()
        for error_hash, occurrences in errors.items():
            for occurrence in occurrences:
                old_time = datetime.now() - timedelta(hours=25)
                occurrence["timestamp"] = old_time.isoformat()
        aggregator._save_errors(errors)

        # Retrieve summary should prune the old error
        summary = aggregator.get_daily_summary()
        assert len(summary) == 0


class TestMetricsCollector:
    """Tests for metrics collection."""

    def test_record_step_execution(self, tmp_path):
        """Test recording step execution."""
        collector = MetricsCollector(storage_path=tmp_path)

        collector.record_step_execution(
            step_id="create", duration_seconds=5.2, success=True
        )

        metrics = collector._load_metrics()
        assert len(metrics["executions"]) == 1
        assert metrics["executions"][0]["step_id"] == "create"
        assert metrics["executions"][0]["duration_seconds"] == 5.2
        assert metrics["executions"][0]["success"] is True

    def test_record_execution_with_metadata(self, tmp_path):
        """Test recording execution with additional metadata."""
        collector = MetricsCollector(storage_path=tmp_path)
        metadata = {"api_latency_ms": 120, "retry_count": 1}

        collector.record_step_execution(
            step_id="share",
            duration_seconds=10.5,
            success=True,
            api_calls=3,
            items_processed=2,
            metadata=metadata,
        )

        metrics = collector._load_metrics()
        execution = metrics["executions"][0]
        assert execution["api_calls"] == 3
        assert execution["items_processed"] == 2
        assert execution["metadata"]["api_latency_ms"] == 120

    def test_get_daily_metrics(self, tmp_path):
        """Test retrieving daily metrics aggregates."""
        collector = MetricsCollector(storage_path=tmp_path)

        collector.record_step_execution("create", 5.0, True)
        collector.record_step_execution("create", 6.0, True)
        collector.record_step_execution("create", 4.0, False)

        daily = collector.get_daily_metrics()

        assert "create" in daily
        assert daily["create"]["executions"] == 3
        assert daily["create"]["successful"] == 2
        assert daily["create"]["failed"] == 1
        assert daily["create"]["success_rate"] == pytest.approx(2 / 3)

    def test_metrics_duration_stats(self, tmp_path):
        """Test that duration statistics are calculated correctly."""
        collector = MetricsCollector(storage_path=tmp_path)

        collector.record_step_execution("create", 5.0, True)
        collector.record_step_execution("create", 10.0, True)
        collector.record_step_execution("create", 15.0, True)

        daily = collector.get_daily_metrics()
        stats = daily["create"]

        assert stats["min_duration_seconds"] == 5.0
        assert stats["max_duration_seconds"] == 15.0
        assert stats["avg_duration_seconds"] == pytest.approx(10.0)

    def test_get_step_history(self, tmp_path):
        """Test retrieving step execution history."""
        collector = MetricsCollector(storage_path=tmp_path)

        for i in range(5):
            collector.record_step_execution("create", float(i + 1), success=i % 2 == 0)

        history = collector.get_step_history("create", limit=3)

        assert len(history) == 3
        assert all(h["step_id"] == "create" for h in history)

    def test_get_overall_stats(self, tmp_path):
        """Test retrieving overall application statistics."""
        collector = MetricsCollector(storage_path=tmp_path)

        collector.record_step_execution("create", 5.0, True, api_calls=2)
        collector.record_step_execution("share", 10.0, True, api_calls=3)
        collector.record_step_execution("notify", 2.0, False, api_calls=1)

        overall = collector.get_overall_stats()

        assert overall["total_executions"] == 3
        assert overall["total_successful"] == 2
        assert overall["total_failed"] == 1
        assert overall["total_api_calls"] == 6
        assert overall["success_rate"] == pytest.approx(2 / 3)

    def test_clear_metrics(self, tmp_path):
        """Test clearing all metrics."""
        collector = MetricsCollector(storage_path=tmp_path)

        collector.record_step_execution("create", 5.0, True)
        assert collector.get_overall_stats()["total_executions"] == 1

        collector.clear_metrics()

        assert collector.get_overall_stats()["total_executions"] == 0

    def test_metrics_time_window(self, tmp_path):
        """Test filtering metrics by time window."""
        collector = MetricsCollector(storage_path=tmp_path)

        collector.record_step_execution("create", 5.0, True)

        # Get metrics from past 24 hours
        daily = collector.get_daily_metrics(hours=24)
        assert "create" in daily

        # Get metrics from past 1 hour (recent should still be there)
        hourly = collector.get_daily_metrics(hours=1)
        assert "create" in hourly


class TestSyslogHandler:
    """Tests for syslog integration."""

    @patch("logging.handlers.SysLogHandler")
    def test_setup_syslog_handler(self, mock_syslog):
        """Test syslog handler setup."""
        mock_instance = MagicMock()
        mock_syslog.return_value = mock_instance

        logger = setup_syslog_handler("skillops")

        assert logger is not None
        assert logger.name == "skillops"
        # Handler may not be added if syslog unavailable, but logger should exist

    @patch("logging.handlers.SysLogHandler")
    def test_syslog_handler_with_custom_facility(self, mock_syslog):
        """Test syslog handler with custom facility."""
        mock_instance = MagicMock()
        mock_syslog.return_value = mock_instance

        logger = setup_syslog_handler("skillops", facility="local0")

        assert logger is not None
        assert logger.name == "skillops"

    def test_syslog_handler_graceful_fallback(self):
        """Test graceful fallback when syslog unavailable."""
        # This test handles case where /dev/log doesn't exist
        logger = setup_syslog_handler("skillops")

        # Should return a logger even if syslog not available
        assert logger is not None
        assert logger.name == "skillops"

    def test_syslog_facility_mapping(self):
        """Test that facility names are correctly mapped."""
        facilities = ["user", "local0", "local1", "local2", "local3"]

        for facility in facilities:
            # Should not raise an error
            logger = setup_syslog_handler("test", facility=facility)
            assert logger is not None
