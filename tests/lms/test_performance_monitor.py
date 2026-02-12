"""Tests for Phase 5 performance monitor."""

from src.lms.performance_monitor import PerformanceMonitor, ThresholdAlert


def _noop():
    return "ok"


def test_record_timing_creates_alert(tmp_path):
    monitor = PerformanceMonitor(thresholds={"op": 0.0}, storage_path=tmp_path)
    alert = monitor.record_timing("op", duration_seconds=0.5)
    assert isinstance(alert, ThresholdAlert)


def test_record_timing_no_alert(tmp_path):
    monitor = PerformanceMonitor(thresholds={"op": 2.0}, storage_path=tmp_path)
    alert = monitor.record_timing("op", duration_seconds=0.5)
    assert alert is None


def test_get_alerts(tmp_path):
    monitor = PerformanceMonitor(thresholds={"op": 0.0}, storage_path=tmp_path)
    monitor.record_timing("op", duration_seconds=0.5)
    alerts = monitor.get_alerts()
    assert len(alerts) == 1


def test_clear_alerts(tmp_path):
    monitor = PerformanceMonitor(thresholds={"op": 0.0}, storage_path=tmp_path)
    monitor.record_timing("op", duration_seconds=0.5)
    monitor.clear_alerts()
    assert monitor.get_alerts() == []


def test_monitor_operation_records(tmp_path):
    monitor = PerformanceMonitor(thresholds={"noop": 0.0}, storage_path=tmp_path)
    payload = monitor.monitor_operation("noop", _noop)
    assert payload["result"] == "ok"
    assert payload["duration_seconds"] >= 0


def test_monitor_operation_alert(tmp_path):
    monitor = PerformanceMonitor(thresholds={"noop": 0.0}, storage_path=tmp_path)
    payload = monitor.monitor_operation("noop", _noop)
    assert isinstance(payload["alert"], ThresholdAlert)
