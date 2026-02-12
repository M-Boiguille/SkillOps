"""Tests for Phase 5 profiling utilities."""

import json

from src.lms.database import init_db, get_connection
from src.lms.performance_profiling import (
    explain_query_plan,
    generate_report,
    profile_cpu,
    profile_memory,
    time_function,
)


def _add(a, b):
    return a + b


def test_time_function_returns_result_and_duration():
    result, duration = time_function(_add, 2, 3)
    assert result == 5
    assert duration >= 0


def test_profile_cpu_returns_stats():
    outcome = profile_cpu(_add, 1, 2)
    assert outcome["result"] == 3
    assert outcome["duration_seconds"] >= 0
    assert "function calls" in outcome["stats"]


def test_profile_memory_returns_payload():
    outcome = profile_memory(_add, 1, 2)
    assert "memory_usage_mb" in outcome
    assert outcome["result"] == 3


def test_explain_query_plan_returns_rows(tmp_path):
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    try:
        rows = explain_query_plan(conn, "SELECT 1")
    finally:
        conn.close()
    assert isinstance(rows, list)
    assert len(rows) > 0


def test_generate_report_json():
    report = generate_report([{"name": "test", "duration_seconds": 0.1}])
    payload = json.loads(report)
    assert payload[0]["name"] == "test"


def test_generate_report_csv():
    report = generate_report(
        [{"name": "test", "duration_seconds": 0.1}], output_format="csv"
    )
    assert "name" in report
    assert "duration_seconds" in report


def test_generate_report_invalid_format():
    try:
        generate_report([{"name": "test"}], output_format="xml")
    except ValueError as exc:
        assert "output_format" in str(exc)
    else:
        assert False, "Expected ValueError for invalid output_format"


def test_profile_memory_duration_field():
    outcome = profile_memory(_add, 2, 2)
    assert "duration_seconds" in outcome
