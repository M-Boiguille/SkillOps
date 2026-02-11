"""Tests for SQLite-backed MetricsCollector."""

from src.lms.monitoring.metrics import MetricsCollector


def test_metrics_collector_records_and_reads(tmp_path):
    collector = MetricsCollector(storage_path=str(tmp_path))

    collector.record_step_execution("create", 1.5, True, api_calls=2, items_processed=3)
    collector.record_step_execution(
        "create", 2.5, False, api_calls=1, items_processed=1
    )
    collector.record_step_execution("notify", 0.5, True, api_calls=0, items_processed=0)

    stats = collector.get_overall_stats()

    assert stats["total_executions"] == 3
    assert stats["total_successful"] == 2
    assert stats["total_failed"] == 1


def test_metrics_collector_daily_metrics(tmp_path):
    collector = MetricsCollector(storage_path=str(tmp_path))

    collector.record_step_execution("create", 1.0, True)
    collector.record_step_execution("create", 2.0, True)

    stats = collector.get_daily_metrics(hours=24)

    assert "create" in stats
    assert stats["create"]["executions"] == 2
    assert stats["create"]["success_rate"] == 1.0


def test_metrics_collector_clear(tmp_path):
    collector = MetricsCollector(storage_path=str(tmp_path))
    collector.record_step_execution("create", 1.0, True)

    collector.clear_metrics()

    stats = collector.get_overall_stats()
    assert stats["total_executions"] == 0
