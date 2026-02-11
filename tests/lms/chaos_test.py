import sqlite3
from datetime import datetime

from src.lms.chaos import ChaosConfig, ChaosEvent, log_chaos_event, run_chaos


def test_log_chaos_event_inserts_row(tmp_path):
    event = ChaosEvent(
        timestamp=datetime.now().isoformat(),
        level=1,
        mode="docker",
        action="kill",
        target="container-1",
        status="success",
        details={"output": "dry-run"},
    )
    log_chaos_event(event, storage_path=tmp_path)

    conn = sqlite3.connect(tmp_path / "skillops.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chaos_events")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1


def test_run_chaos_dry_run_level1(tmp_path):
    config = ChaosConfig(
        level=1,
        mode="docker",
        only_once=True,
        execute=False,
    )

    events = run_chaos(
        config,
        storage_path=tmp_path,
        targets=["container-1"],
    )

    assert len(events) == 1
    assert events[0].status == "success"

    conn = sqlite3.connect(tmp_path / "skillops.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chaos_events")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1
