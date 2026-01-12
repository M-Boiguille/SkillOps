"""Tests for mission generator."""

import pytest
from src.lms.integrations.mission_generator import MissionGenerator


@pytest.fixture
def generator():
    """Create mission generator (with mock if no API key)."""
    try:
        return MissionGenerator()
    except ValueError:
        # Skip tests if API key not available
        pytest.skip("GEMINI_API_KEY not set")


class TestMissionGenerator:
    """Tests for MissionGenerator."""

    def test_available_roles(self):
        """Test available roles."""
        roles = MissionGenerator.get_available_roles()

        assert isinstance(roles, dict)
        assert len(roles) > 0
        assert "cloud_engineer" in roles
        assert "sre" in roles
        assert "cicd_specialist" in roles

    def test_role_structure(self):
        """Test role structure."""
        roles = MissionGenerator.get_available_roles()

        for role_key, role_info in roles.items():
            assert "title" in role_info
            assert "description" in role_info
            assert "tech_stacks" in role_info
            assert isinstance(role_info["tech_stacks"], list)

    def test_validate_mission_feasibility_good(self, generator):
        """Test mission feasibility check - good case."""
        mission = {
            "project_name": "Simple Python CLI",
            "learning_needs": [
                {"skill": "Python", "hours": 5, "priority": "low"},
                {"skill": "Click", "hours": 3, "priority": "low"},
            ],
        }

        is_feasible, missing = generator.validate_mission_feasibility(
            mission, ["Python"]
        )

        assert is_feasible is True
        assert len(missing) == 0

    def test_validate_mission_feasibility_too_many_gaps(self, generator):
        """Test mission feasibility check - too many learning needs."""
        mission = {
            "project_name": "Complex Infrastructure",
            "learning_needs": [
                {"skill": "Kubernetes", "hours": 40, "priority": "high"},
                {"skill": "Terraform", "hours": 30, "priority": "high"},
                {"skill": "AWS", "hours": 25, "priority": "high"},
                {"skill": "Prometheus", "hours": 20, "priority": "high"},
            ],
        }

        is_feasible, missing = generator.validate_mission_feasibility(
            mission, ["Docker"]
        )

        assert is_feasible is False
        assert len(missing) > 0

    def test_mission_response_parsing(self, generator):
        """Test parsing of mission response."""
        response_text = """{
            "project_name": "Test Project",
            "project_description": "A test project",
            "tech_stack": ["Python", "Docker"],
            "scope": ["Feature 1", "Feature 2"],
            "learning_needs": [],
            "mvp_features": ["Core"],
            "excellence_features": [],
            "success_criteria": ["Tests pass"],
            "estimated_hours": 20
        }"""

        parsed = generator._parse_mission_response(response_text)

        assert parsed["project_name"] == "Test Project"
        assert "Python" in parsed["tech_stack"]
        assert parsed["estimated_hours"] == 20

    def test_mission_response_parsing_with_markdown(self, generator):
        """Test parsing of mission response with markdown code blocks."""
        response_text = """```json
{
    "project_name": "Test Project",
    "project_description": "A test project",
    "tech_stack": ["Python"],
    "scope": [],
    "learning_needs": [],
    "mvp_features": [],
    "excellence_features": [],
    "success_criteria": [],
    "estimated_hours": 20
}
```"""

        parsed = generator._parse_mission_response(response_text)

        assert parsed["project_name"] == "Test Project"
        assert parsed["estimated_hours"] == 20

    def test_ai_suggested_prompt_building(self, generator):
        """Test AI-suggested prompt building."""
        role_info = MissionGenerator.ROLES["cloud_engineer"]
        prompt = generator._build_ai_suggested_prompt(
            "cloud_engineer", role_info, "intermediate", ["Docker", "AWS"]
        )

        assert "cloud_engineer" in prompt.lower() or "cloud" in prompt.lower()
        assert "intermediate" in prompt.lower()
        assert "Docker" in prompt
        assert "JSON" in prompt

    def test_po_prompt_building(self, generator):
        """Test Product Owner prompt building."""
        prompt = generator._build_po_prompt(
            "backend_engineer", "junior", ["Python"], "I want to build a REST API"
        )

        assert "backend" in prompt.lower()
        assert "junior" in prompt.lower()
        assert "REST API" in prompt
        assert "JSON" in prompt
