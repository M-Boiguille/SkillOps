"""Tests for oncall AI generation module."""

from unittest.mock import MagicMock, patch

from src.lms.oncall_ai import (
    calculate_next_review_date,
    get_due_incidents,
    get_incident_context,
)


def test_get_incident_context(tmp_path):
    """Test building incident context from database."""
    context = get_incident_context(storage_path=tmp_path)

    assert context is not None
    assert hasattr(context, "past_postmortems")
    assert hasattr(context, "weak_areas")
    assert hasattr(context, "skill_level")
    assert context.skill_level in ["beginner", "intermediate", "advanced"]


def test_calculate_next_review_date():
    """Test SRS scheduling algorithm."""
    from datetime import datetime, timedelta

    # Score 0: immediate retry (0 days)
    date_0 = calculate_next_review_date(0)
    expected_0 = datetime.now().date().isoformat()
    assert date_0 == expected_0

    # Score 1-2: 1 day
    date_1 = calculate_next_review_date(1)
    expected_1 = (datetime.now() + timedelta(days=1)).date().isoformat()
    assert date_1 == expected_1

    # Score 3: 3 days
    date_3 = calculate_next_review_date(3)
    expected_3 = (datetime.now() + timedelta(days=3)).date().isoformat()
    assert date_3 == expected_3

    # Score 4: 7 days
    date_4 = calculate_next_review_date(4)
    expected_4 = (datetime.now() + timedelta(days=7)).date().isoformat()
    assert date_4 == expected_4

    # Score 5: 14 days
    date_5 = calculate_next_review_date(5)
    expected_5 = (datetime.now() + timedelta(days=14)).date().isoformat()
    assert date_5 == expected_5


def test_get_due_incidents_empty(tmp_path):
    """Test getting due incidents with empty database."""
    due = get_due_incidents(storage_path=tmp_path)
    assert due == []


@patch("src.lms.oncall_ai.genai.Client")
def test_generate_incident_with_mock_api(mock_client, tmp_path, monkeypatch):
    """Test AI incident generation with mocked Gemini API."""
    from src.lms.oncall_ai import generate_incident_with_ai

    # Mock environment variable
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    # Mock Gemini response
    mock_response = MagicMock()
    mock_response.text = """```json
{
  "severity": "P2",
  "title": "High CPU usage on web servers",
  "description": "CPU usage at 95% on production web servers",
  "affected_system": "Docker",
  "symptoms": "Slow response times, high load average",
  "hints": ["Check process list", "Review container limits", "Scale horizontally"]
}
```"""

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Generate incident
    incident_data = generate_incident_with_ai(storage_path=tmp_path)

    assert incident_data is not None
    assert incident_data["severity"] == "P2"
    assert incident_data["title"] == "High CPU usage on web servers"
    assert incident_data["generated_by"] == "ai"
    assert "hints" in incident_data
    assert len(incident_data["hints"]) == 3


@patch("src.lms.oncall_ai.genai.Client")
def test_generate_hints_with_mock_api(mock_client, tmp_path, monkeypatch):
    """Test progressive hints generation."""
    from src.lms.oncall_ai import generate_hints_for_incident
    from src.lms.oncall import create_incident

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    # Create a test incident
    with patch("src.lms.oncall.generate_incident_with_ai") as mock_gen:
        mock_gen.return_value = {
            "severity": "P1",
            "title": "Test",
            "description": "Test",
            "affected_system": "Test",
            "symptoms": "Test",
            "difficulty_level": 1,
            "generated_by": "ai",
        }
        incident = create_incident(storage_path=tmp_path, use_ai=True)

    # Mock hint generation
    mock_response = MagicMock()
    mock_response.text = "What component manages container orchestration?"

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Generate hint
    hint = generate_hints_for_incident(incident.id, 1, storage_path=tmp_path)

    assert hint is not None
    assert len(hint) > 0
