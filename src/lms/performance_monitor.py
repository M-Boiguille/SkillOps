"""Performance monitoring utilities for Phase 5."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable, Dict, List, Optional

from src.lms.monitoring.metrics import MetricsCollector


@dataclass
class ThresholdAlert:
    name: str
    value_seconds: float
    threshold_seconds: float
    message: str


class PerformanceMonitor:
    """Monitor durations against thresholds and record metrics."""

    def __init__(
        self, thresholds: Optional[Dict[str, float]] = None, storage_path=None
    ):
        self.thresholds = thresholds or {}
        self._alerts: List[ThresholdAlert] = []
        self.metrics = MetricsCollector(storage_path=storage_path)

    def record_timing(
        self,
        name: str,
        duration_seconds: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ThresholdAlert]:
        self.metrics.record_step_execution(
            step_id=name,
            duration_seconds=duration_seconds,
            success=success,
            metadata=metadata or {},
        )
        return self._check_threshold(name, duration_seconds)

    def _check_threshold(
        self, name: str, duration_seconds: float
    ) -> Optional[ThresholdAlert]:
        threshold = self.thresholds.get(name)
        if threshold is None:
            return None
        if duration_seconds <= threshold:
            return None
        alert = ThresholdAlert(
            name=name,
            value_seconds=duration_seconds,
            threshold_seconds=threshold,
            message=(
                f"{name} exceeded threshold: {duration_seconds:.3f}s > {threshold:.3f}s"
            ),
        )
        self._alerts.append(alert)
        return alert

    def get_alerts(self) -> List[ThresholdAlert]:
        return list(self._alerts)

    def clear_alerts(self) -> None:
        self._alerts = []

    def monitor_operation(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        start = perf_counter()
        result = func(*args, **kwargs)
        duration = perf_counter() - start
        alert = self.record_timing(
            name=name,
            duration_seconds=duration,
            success=True,
            metadata=metadata,
        )
        return {
            "result": result,
            "duration_seconds": duration,
            "alert": alert,
        }
