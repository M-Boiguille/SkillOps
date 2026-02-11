"""Tests for oncall module."""

from src.lms.oncall import (
    create_incident,
    get_open_incidents,
    update_incident_status,
)


def test_create_incident(tmp_path):
    """Test incident creation."""
    template = {
        "severity": "P1",
        "title": "Test incident",
        "description": "Test description",
        "affected_system": "Test system",
        "symptoms": "Test symptoms",
    }

    incident = create_incident(storage_path=tmp_path, template=template)

    assert incident.id is not None
    assert incident.severity == "P1"
    assert incident.title == "Test incident"
    assert incident.status == "open"


def test_get_open_incidents(tmp_path):
    """Test retrieving open incidents."""
    template = {
        "severity": "P2",
        "title": "Open incident",
        "description": "Test",
        "affected_system": "System",
        "symptoms": "Symptoms",
    }

    create_incident(storage_path=tmp_path, template=template)
    incidents = get_open_incidents(storage_path=tmp_path)

    assert len(incidents) == 1
    assert incidents[0].status == "open"


def test_update_incident_status(tmp_path):
    """Test updating incident status."""
    template = {
        "severity": "P3",
        "title": "Incident to resolve",
        "description": "Test",
        "affected_system": "System",
        "symptoms": "Symptoms",
    }

    incident = create_incident(storage_path=tmp_path, template=template)
    update_incident_status(
        incident.id, "resolved", "Fixed by restarting service", tmp_path
    )

    incidents = get_open_incidents(storage_path=tmp_path)
    assert len(incidents) == 0
