"""Performance profiling utilities for SkillOps."""

from __future__ import annotations

import cProfile
import csv
import io
import json
import pstats
from time import perf_counter
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


def time_function(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Tuple[Any, float]:
    """Run a function and measure duration."""
    start = perf_counter()
    result = func(*args, **kwargs)
    duration = perf_counter() - start
    return result, duration


def profile_cpu(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Profile CPU usage for a function using cProfile."""
    profiler = cProfile.Profile()
    start = perf_counter()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    duration = perf_counter() - start

    stats_buffer = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_buffer).sort_stats("cumulative")
    stats.print_stats(20)

    return {
        "result": result,
        "duration_seconds": duration,
        "stats": stats_buffer.getvalue(),
    }


def profile_memory(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    """Profile memory usage for a function (if memory_profiler is available)."""
    try:
        from memory_profiler import memory_usage
    except Exception:
        result, duration = time_function(func, *args, **kwargs)
        return {
            "result": result,
            "duration_seconds": duration,
            "memory_usage_mb": None,
        }

    def _runner() -> Any:
        return func(*args, **kwargs)

    start = perf_counter()
    usage, result = memory_usage(_runner, max_usage=True, retval=True)
    duration = perf_counter() - start
    return {
        "result": result,
        "duration_seconds": duration,
        "memory_usage_mb": float(usage),
    }


def explain_query_plan(
    conn, query: str, params: Optional[Iterable[Any]] = None
) -> List[tuple]:
    """Return SQLite EXPLAIN QUERY PLAN output for a query."""
    cursor = conn.cursor()
    cursor.execute(f"EXPLAIN QUERY PLAN {query}", params or ())
    return cursor.fetchall()


def generate_report(entries: List[Dict[str, Any]], output_format: str = "json") -> str:
    """Generate JSON or CSV report from profiling entries."""
    if output_format == "json":
        return json.dumps(entries, indent=2, default=str)

    if output_format != "csv":
        raise ValueError("output_format must be 'json' or 'csv'")

    if not entries:
        return ""

    fieldnames = sorted({key for entry in entries for key in entry.keys()})
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for entry in entries:
        writer.writerow(entry)
    return buffer.getvalue()
