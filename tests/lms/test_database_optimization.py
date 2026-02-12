"""Tests for Phase 5 database optimization helpers."""

import sqlite3

from src.lms.cache import TTLCache
from src.lms.database import get_connection, init_db
from src.lms.database_optimization import (
    ConnectionPool,
    analyze_query_plan,
    ensure_code_session_indexes,
    ensure_tracking_indexes,
    vacuum_db,
)


def test_ensure_tracking_indexes(tmp_path):
    init_db(tmp_path)
    ensure_tracking_indexes(tmp_path)
    conn = get_connection(tmp_path)
    try:
        cursor = conn.execute("PRAGMA index_list(tracking_summary)")
        indexes = {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()
    assert "idx_tracking_summary_date" in indexes
    assert "idx_tracking_summary_date_activity" in indexes
    assert "idx_tracking_summary_date_commits" in indexes


def test_ensure_code_session_indexes(tmp_path):
    init_db(tmp_path)
    ensure_code_session_indexes(tmp_path)
    conn = get_connection(tmp_path)
    try:
        cursor = conn.execute("PRAGMA index_list(code_sessions)")
        indexes = {row[1] for row in cursor.fetchall()}
    finally:
        conn.close()
    assert "idx_code_sessions_date" in indexes
    assert "idx_code_sessions_commit_time" in indexes


def test_analyze_query_plan(tmp_path):
    init_db(tmp_path)
    rows = analyze_query_plan("SELECT 1", storage_path=tmp_path)
    assert len(rows) > 0


def test_connection_pool_acquire_release(tmp_path):
    pool = ConnectionPool(storage_path=tmp_path, max_size=1)
    conn = pool.acquire()
    assert isinstance(conn, sqlite3.Connection)
    pool.release(conn)


def test_connection_pool_max_size(tmp_path):
    pool = ConnectionPool(storage_path=tmp_path, max_size=1)
    conn = pool.acquire()
    try:
        try:
            pool.acquire()
        except RuntimeError:
            assert True
        else:
            assert False, "Expected RuntimeError when pool exhausted"
    finally:
        pool.release(conn)


def test_vacuum_db(tmp_path):
    init_db(tmp_path)
    vacuum_db(tmp_path)


def test_cache_set_get_hit():
    cache = TTLCache(default_ttl_seconds=60)
    cache.set("key", "value")
    assert cache.get("key") == "value"
    assert cache.stats.hits == 1


def test_cache_miss():
    cache = TTLCache(default_ttl_seconds=60)
    assert cache.get("missing") is None
    assert cache.stats.misses == 1


def test_cache_expiration():
    cache = TTLCache(default_ttl_seconds=0)
    cache.set("key", "value")
    assert cache.get("key") is None


def test_cache_clear_resets_stats():
    cache = TTLCache(default_ttl_seconds=60)
    cache.set("key", "value")
    cache.get("key")
    cache.clear()
    assert cache.stats.hits == 0
    assert cache.stats.misses == 0
