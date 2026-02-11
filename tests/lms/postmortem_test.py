"""Tests for postmortem module."""

from src.lms.postmortem import get_postmortem, list_postmortems
from src.lms.database import get_connection, init_db


def test_create_postmortem_db(tmp_path):
    """Test post-mortem storage in database."""
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO incidents (timestamp, severity, title, description,
                               affected_system, symptoms, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "2026-02-11T14:00:00",
            "P1",
            "Test incident",
            "Description",
            "System",
            "Symptoms",
            "open",
        ),
    )
    incident_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO postmortems
        (incident_id, timestamp, what_happened, when_detected, impact,
         root_cause, resolution, prevention, action_items)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident_id,
            "2026-02-11T15:00:00",
            "Database crashed",
            "14:00",
            "Users couldn't login",
            "Disk full",
            "Cleared logs",
            "Implement log rotation",
            '["Add disk alerts", "Enable log rotation"]',
        ),
    )
    postmortem_id = cursor.lastrowid
    conn.commit()
    conn.close()

    postmortem = get_postmortem(postmortem_id, tmp_path)
    assert postmortem is not None
    assert postmortem.what_happened == "Database crashed"
    assert postmortem.incident_id == incident_id


def test_list_postmortems(tmp_path):
    """Test listing all post-mortems."""
    init_db(tmp_path)
    conn = get_connection(tmp_path)
    cursor = conn.cursor()

    # Create incidents first
    for i in range(2):
        cursor.execute(
            """
            INSERT INTO incidents (timestamp, severity, title, description,
                                   affected_system, symptoms, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"2026-02-11T{10+i}:00:00",
                "P2",
                f"Incident {i}",
                "Desc",
                "System",
                "Symptoms",
                "open",
            ),
        )
        incident_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO postmortems
            (incident_id, timestamp, what_happened, when_detected, impact,
             root_cause, resolution, prevention, action_items)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident_id,
                f"2026-02-11T{11+i}:00:00",
                f"Issue {i}",
                "10:00",
                "Impact",
                "Cause",
                "Fix",
                "Prevention",
                "[]",
            ),
        )

    conn.commit()
    conn.close()

    postmortems = list_postmortems(tmp_path)
    assert len(postmortems) == 2
