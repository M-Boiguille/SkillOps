"""Tests for Phase 5 tracking optimizations."""

import pytest

from src.lms.database import get_connection, init_db
from src.lms.tracking_optimization import (
    batch_insert_code_sessions,
    chunked,
    reduce_tracking_data,
    stream_tracking_summary,
)


def _insert_tracking_summary(conn, date_str: str):
    conn.execute(
        """
        INSERT OR REPLACE INTO tracking_summary
        (date, wakatime_seconds, git_commits, git_files_changed,
         git_lines_added, git_lines_deleted, activity_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (date_str, 3600, 2, 1, 10, 5, "medium"),
    )
    conn.commit()


def test_batch_insert_code_sessions(tmp_path):
    init_db(tmp_path)
    commits = [
        {
            "commit_hash": "abc",
            "commit_time": "2026-02-12T10:00:00Z",
            "commit_msg": "Test",
            "files_changed": 1,
            "lines_added": 5,
            "lines_deleted": 2,
        }
    ]
    inserted = batch_insert_code_sessions(commits, storage_path=tmp_path)
    assert inserted == 1

    conn = get_connection(tmp_path)
    try:
        count = conn.execute("SELECT COUNT(*) FROM code_sessions").fetchone()[0]
    finally:
        conn.close()
    assert count == 1


def test_batch_insert_code_sessions_empty(tmp_path):
    init_db(tmp_path)
    inserted = batch_insert_code_sessions([], storage_path=tmp_path)
    assert inserted == 0


def test_batch_insert_missing_fields(tmp_path):
    init_db(tmp_path)
    with pytest.raises(ValueError):
        batch_insert_code_sessions([{"commit_hash": "x"}], storage_path=tmp_path)


def test_stream_tracking_summary(tmp_path):
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    try:
        _insert_tracking_summary(conn, "2026-02-12")
    finally:
        conn.close()

    results = list(stream_tracking_summary(days=7, storage_path=tmp_path))
    assert len(results) >= 1
    assert results[0]["activity_level"] == "medium"


def test_reduce_tracking_data():
    data = [{"date": str(i)} for i in range(5)]
    trimmed = reduce_tracking_data(data, max_days=2)
    assert len(trimmed) == 2


def test_chunked_iterable():
    chunks = list(chunked([1, 2, 3, 4, 5], size=2))
    assert chunks == [[1, 2], [3, 4], [5]]


def test_stream_tracking_summary_respects_days(tmp_path):
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    try:
        _insert_tracking_summary(conn, "2026-02-12")
        _insert_tracking_summary(conn, "2026-02-10")
    finally:
        conn.close()
    results = list(stream_tracking_summary(days=1, storage_path=tmp_path))
    assert len(results) <= 1


def test_batch_insert_multiple_rows(tmp_path):
    init_db(tmp_path)
    commits = []
    for idx in range(2):
        commits.append(
            {
                "commit_hash": f"hash_{idx}",
                "commit_time": "2026-02-12T10:00:00Z",
                "commit_msg": "Test",
                "files_changed": 1,
                "lines_added": 5,
                "lines_deleted": 2,
            }
        )
    inserted = batch_insert_code_sessions(commits, storage_path=tmp_path)
    assert inserted == 2
