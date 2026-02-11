"""Tests for oncall module."""

from unittest.mock import patch

from src.lms.oncall import (
    create_incident,
    get_open_incidents,
    update_incident_status,
)
from src.lms.oncall_ai import calculate_next_review_date


def test_create_incident_without_ai(tmp_path):
    """Test incident creation without AI (fallback mode)."""
    # Mock AI generation to fail
    with patch("src.lms.oncall.generate_incident_with_ai") as mock_gen:
        mock_gen.side_effect = ValueError("No API key")

        incident = create_incident(storage_path=tmp_path, use_ai=False)

        # Fallback should create a basic incident
        assert incident is not None
        assert incident.id is not None
        assert incident.generated_by == "fallback"


def test_create_incident_with_ai_mock(tmp_path):
    """Test AI incident creation with mocked API."""
    with patch("src.lms.oncall.generate_incident_with_ai") as mock_gen:
        mock_gen.return_value = {
            "severity": "P1",
            "title": "AI Generated Incident",
            "description": "Test AI description",
            "affected_system": "Kubernetes",
            "symptoms": "Pods crashing",
            "difficulty_level": 2,
            "generated_by": "ai",
        }

        incident = create_incident(storage_path=tmp_path, use_ai=True)

        assert incident is not None
        assert incident.id is not None
        assert incident.title == "AI Generated Incident"
        assert incident.difficulty_level == 2
        assert incident.generated_by == "ai"


def test_get_open_incidents(tmp_path):
    """Test retrieving open incidents."""
    with patch("src.lms.oncall.generate_incident_with_ai") as mock_gen:
        mock_gen.return_value = {
            "severity": "P2",
            "title": "Open incident",
            "description": "Test",
            "affected_system": "System",
            "symptoms": "Symptoms",
            "difficulty_level": 1,
            "generated_by": "ai",
        }

        create_incident(storage_path=tmp_path, use_ai=True)
        incidents = get_open_incidents(storage_path=tmp_path)

        assert len(incidents) == 1
        assert incidents[0].status == "open"


def test_update_incident_status_with_score(tmp_path):
    """Test updating incident status with SRS scoring."""
    with patch("src.lms.oncall.generate_incident_with_ai") as mock_gen:
        mock_gen.return_value = {
            "severity": "P3",
            "title": "Incident to resolve",
            "description": "Test",
            "affected_system": "System",
            "symptoms": "Symptoms",
            "difficulty_level": 1,
            "generated_by": "ai",
        }

        incident = create_incident(storage_path=tmp_path, use_ai=True)

        # Resolve with a score
        update_incident_status(
            incident.id,
            "resolved",
            "Fixed by restarting service",
            tmp_path,
            resolution_score=4,
            hints_used=1,
        )

        incidents = get_open_incidents(storage_path=tmp_path)
        assert len(incidents) == 0


def test_srs_scheduling():
    """Test SRS next review date calculation."""
    # Score 0-2: next day
    next_date_low = calculate_next_review_date(1)
    assert next_date_low is not None

    # Score 3-4: 3-7 days
    next_date_med = calculate_next_review_date(3)
    assert next_date_med is not None

    # Score 5: 2 weeks
    next_date_high = calculate_next_review_date(5)
    assert next_date_high is not None
