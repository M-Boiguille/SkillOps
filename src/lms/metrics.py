"""Phase 5 metrics collection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Dict, Optional

from src.lms.monitoring.metrics import MetricsCollector


@dataclass
class TimedOperation:
    """Simple record for an operation timing."""

    name: str
    duration_seconds: float
    success: bool
    metadata: Dict[str, Any]


def record_timed_operation(
    name: str,
    func: Callable[..., Any],
    *args: Any,
    storage_path: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> TimedOperation:
    """Time a function and record metrics to the database."""
    start = perf_counter()
    try:
        func(*args, **kwargs)
        success = True
    except Exception:
        success = False
        raise
    finally:
        duration = perf_counter() - start
        collector = MetricsCollector(storage_path=storage_path)
        collector.record_step_execution(
            step_id=name,
            duration_seconds=duration,
            success=success,
            metadata=metadata or {},
        )

    return TimedOperation(
        name=name,
        duration_seconds=duration,
        success=success,
        metadata=metadata or {},
    )


def collect_dashboard_metrics(
    retrieval_seconds: float,
    render_seconds: float,
    items: int,
) -> Dict[str, Any]:
    """Build a dashboard metrics payload."""
    return {
        "retrieval_seconds": retrieval_seconds,
        "render_seconds": render_seconds,
        "items": items,
        "total_seconds": retrieval_seconds + render_seconds,
    }
