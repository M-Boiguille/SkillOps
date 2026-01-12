"""Tests for mission evaluator."""

import pytest
from src.lms.integrations.mission_evaluator import MissionEvaluator


@pytest.fixture
def evaluator():
    """Create mission evaluator (with mock if no API key)."""
    try:
        return MissionEvaluator()
    except ValueError:
        pytest.skip("GEMINI_API_KEY not set")


@pytest.fixture
def sample_mission_spec():
    """Sample mission specification."""
    return {
        "project_name": "Cloud Monitoring Stack",
        "project_description": "Build observability platform",
        "tech_stack": ["Prometheus", "Grafana", "AlertManager"],
        "mvp_features": ["Metrics collection", "Dashboards", "Alerts"],
        "success_criteria": ["90% uptime", "Sub-second queries", "Documented"],
    }


class TestMissionEvaluator:
    """Tests for MissionEvaluator."""

    def test_evaluate_score_to_level_junior(self, evaluator):
        """Test score to level conversion - junior."""
        assert MissionEvaluator.calculate_level_from_score(30) == "junior"

    def test_evaluate_score_to_level_intermediate(self, evaluator):
        """Test score to level conversion - intermediate."""
        assert MissionEvaluator.calculate_level_from_score(60) == "intermediate"

    def test_evaluate_score_to_level_senior(self, evaluator):
        """Test score to level conversion - senior."""
        assert MissionEvaluator.calculate_level_from_score(85) == "senior"

    def test_score_to_stars_conversion(self, evaluator):
        """Test score to stars conversion."""
        assert MissionEvaluator.calculate_stars(15) == 1
        assert MissionEvaluator.calculate_stars(35) == 2
        assert MissionEvaluator.calculate_stars(55) == 3
        assert MissionEvaluator.calculate_stars(75) == 4
        assert MissionEvaluator.calculate_stars(95) == 5

    def test_evaluation_response_parsing(self, evaluator):
        """Test parsing of evaluation response."""
        response_text = """{
            "overall_score": 82,
            "level_achieved": "intermediate",
            "stars": 4,
            "scores": {
                "completeness": 18,
                "code_quality": 20,
                "testing": 17,
                "devops_practices": 18,
                "documentation": 12
            },
            "strengths": ["Good architecture", "Well tested"],
            "improvements": ["Add monitoring", "Improve docs"],
            "feedback": "Solid project",
            "next_steps": ["Add alerting"]
        }"""

        parsed = evaluator._parse_evaluation_response(response_text)

        assert parsed["overall_score"] == 82
        assert parsed["level_achieved"] == "intermediate"
        assert parsed["stars"] == 4
        assert len(parsed["strengths"]) > 0

    def test_evaluation_response_parsing_with_markdown(self, evaluator):
        """Test parsing with markdown code blocks."""
        response_text = """```json
{
    "overall_score": 75,
    "level_achieved": "intermediate",
    "stars": 4,
    "scores": {},
    "strengths": [],
    "improvements": [],
    "feedback": "Good work",
    "next_steps": []
}
```"""

        parsed = evaluator._parse_evaluation_response(response_text)

        assert parsed["overall_score"] == 75

    def test_evaluation_prompt_building(self, evaluator, sample_mission_spec):
        """Test evaluation prompt building."""
        project_info = {
            "path": "/tmp/test",
            "has_readme": True,
            "has_dockerfile": False,
            "has_ci_cd": True,
            "has_tests": True,
            "has_git": True,
            "files": {},
            "code_stats": {"total_lines": 500, "test_files": 3},
        }

        prompt = evaluator._build_evaluation_prompt(
            sample_mission_spec, project_info, "intermediate"
        )

        assert "Cloud Monitoring Stack" in prompt
        assert "Prometheus" in prompt
        assert "INTERMEDIATE" in prompt
        assert "JSON" in prompt

    def test_collect_project_info_nonexistent(self, evaluator):
        """Test project info collection for nonexistent path."""
        info = evaluator._collect_project_info("/nonexistent/path")

        assert "error" in info

    def test_file_structure_analysis(self, evaluator, tmp_path):
        """Test file structure analysis."""
        # Create test files
        (tmp_path / "main.py").touch()
        (tmp_path / "test_main.py").touch()
        (tmp_path / "README.md").touch()

        info = evaluator._analyze_file_structure(tmp_path)

        assert ".py" in info
        assert ".md" in info
        assert info[".py"] >= 2

    def test_code_stats_analysis(self, evaluator, tmp_path):
        """Test code statistics analysis."""
        # Create test files with content
        (tmp_path / "app.py").write_text("def hello():\n    print('hello')\n")
        (tmp_path / "test_app.py").write_text("def test_hello():\n    pass\n")

        stats = evaluator._analyze_code_stats(tmp_path)

        assert stats["total_lines"] > 0
        assert stats["test_files"] >= 1

    def test_default_evaluation_on_parse_error(self, evaluator):
        """Test fallback evaluation on parse error."""
        bad_response = "This is not JSON {{{[ invalid"

        parsed = evaluator._parse_evaluation_response(bad_response)

        assert "overall_score" in parsed
        assert parsed["overall_score"] == 50  # Default score
        assert "junior" in parsed["level_achieved"]
