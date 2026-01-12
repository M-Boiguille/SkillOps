"""Tests for the Labs Fictive step."""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.lms.steps.labs import (
    get_storage_path,
    get_missions_dir,
    get_profiles_dir,
    select_role,
    profile_learner,
    generate_or_suggest_mission,
    display_mission_details,
    save_mission,
    evaluate_mission,
    award_progression,
    AVAILABLE_ROLES,
)


class TestStoragePaths:
    """Test storage path retrieval functions."""

    def test_get_storage_path_uses_env_var(self):
        """Storage path should use STORAGE_PATH env var if set."""
        with patch.dict(os.environ, {"STORAGE_PATH": "/custom/path"}):
            path = get_storage_path()
            assert path == Path("/custom/path")

    def test_get_storage_path_default(self):
        """Storage path should default to ~/.local/share/skillops."""
        with patch.dict(os.environ, {}, clear=False):
            if "STORAGE_PATH" in os.environ:
                del os.environ["STORAGE_PATH"]
            path = get_storage_path()
            assert "skillops" in str(path)

    def test_get_missions_dir_creates_directory(self, tmp_path):
        """Missions directory should be created if not exists."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            missions_dir = get_missions_dir()
            assert missions_dir.exists()
            assert "missions" in str(missions_dir)

    def test_get_profiles_dir_creates_directory(self, tmp_path):
        """Profiles directory should be created if not exists."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            profiles_dir = get_profiles_dir()
            assert profiles_dir.exists()
            assert "profiles" in str(profiles_dir)


class TestRoleSelection:
    """Test role selection functionality."""

    def test_select_role_validates_choices(self):
        """Role selection should only accept valid roles."""
        assert all(role in AVAILABLE_ROLES for role in AVAILABLE_ROLES)
        assert len(AVAILABLE_ROLES) >= 6

    def test_available_roles_structure(self):
        """Available roles should contain common DevOps roles."""
        expected_roles = [
            "cloud_engineer",
            "sre",
            "cicd_specialist",
            "backend_engineer",
            "devops_engineer",
            "infrastructure_engineer",
        ]
        assert set(expected_roles).issubset(set(AVAILABLE_ROLES))


class TestLearnerProfiling:
    """Test learner profiling functionality."""

    @patch("src.lms.steps.labs.LearnerProfiler")
    def test_profile_learner_success(self, mock_profiler_class):
        """Learner profiling should return profile data on success."""
        # Setup mock profiler
        mock_profiler = Mock()
        mock_profiler_class.return_value = mock_profiler

        profile_data = {
            "level": "intermediate",
            "overall_score": 75.5,
            "reinforce_score": 80.0,
            "anki_score": 70.0,
            "github_score": 75.0,
            "self_score": 76.0,
        }
        mock_profiler.evaluate_learner_level.return_value = profile_data
        mock_profiler.is_ready_for_mission.return_value = True

        with patch("src.lms.steps.labs.console"):
            result = profile_learner()

        assert result == profile_data

    @patch("src.lms.steps.labs.LearnerProfiler")
    def test_profile_learner_not_ready(self, mock_profiler_class):
        """Profiler should return None if learner not ready."""
        mock_profiler = Mock()
        mock_profiler_class.return_value = mock_profiler

        profile_data = {
            "level": "junior",
            "overall_score": 45.0,
            "reinforce_score": 40.0,
            "anki_score": 50.0,
            "github_score": 40.0,
            "self_score": 50.0,
        }
        mock_profiler.evaluate_learner_level.return_value = profile_data
        mock_profiler.is_ready_for_mission.return_value = False

        with patch("src.lms.steps.labs.console"):
            result = profile_learner()

        assert result is None

    @patch("src.lms.steps.labs.LearnerProfiler")
    def test_profile_learner_exception(self, mock_profiler_class):
        """Profiler should return None on exception."""
        mock_profiler = Mock()
        mock_profiler_class.return_value = mock_profiler
        mock_profiler.evaluate_learner_level.side_effect = Exception(
            "Test error"
        )

        with patch("src.lms.steps.labs.console"):
            result = profile_learner()

        assert result is None


class TestMissionGeneration:
    """Test mission generation functionality."""

    @patch("src.lms.steps.labs.MissionGenerator")
    @patch("src.lms.steps.labs.Prompt")
    def test_generate_mission_ai_suggested(
        self, mock_prompt, mock_generator_class
    ):
        """AI-suggested mode should generate mission based on learner level."""
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        mission_data = {
            "project_name": "Kubernetes Deployment Pipeline",
            "project_description": "Build a K8s deployment pipeline",
            "tech_stack": ["kubernetes", "docker", "helm"],
            "scope": ["setup", "deploy"],
            "estimated_hours": 40,
        }
        mock_generator.generate_mission.return_value = mission_data
        mock_prompt.ask.return_value = "1"  # AI-suggested mode

        profile = {
            "level": "intermediate",
            "skills": ["docker", "bash"],
        }

        with patch("src.lms.steps.labs.console"):
            result = generate_or_suggest_mission(profile, "sre")

        assert result == mission_data
        mock_generator.generate_mission.assert_called_once()

    @patch("src.lms.steps.labs.MissionGenerator")
    @patch("src.lms.steps.labs.Prompt")
    def test_generate_mission_po_mode(self, mock_prompt, mock_generator_class):
        """Product Owner mode should accept user idea."""
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        mission_data = {
            "project_name": "Custom DevOps Project",
            "project_description": "User idea transformed",
            "tech_stack": [],
            "scope": [],
            "estimated_hours": 40,
        }
        mock_generator.generate_mission.return_value = mission_data

        # Setup prompts: mode = "2", user_idea
        mock_prompt.ask.side_effect = ["2", "Build a CI/CD pipeline"]

        profile = {
            "level": "intermediate",
            "skills": ["docker"],
        }

        with patch("src.lms.steps.labs.console"):
            result = generate_or_suggest_mission(profile, "cicd_specialist")

        assert result == mission_data

    @patch("src.lms.steps.labs.MissionGenerator")
    @patch("src.lms.steps.labs.Prompt")
    def test_generate_mission_empty_idea(
        self, mock_prompt, mock_generator_class
    ):
        """Empty user idea should be rejected."""
        mock_prompt.ask.side_effect = ["2", "   "]  # whitespace only

        profile = {"level": "intermediate", "skills": []}

        with patch("src.lms.steps.labs.console"):
            result = generate_or_suggest_mission(profile, "backend_engineer")

        assert result is None


class TestMissionDisplay:
    """Test mission display functionality."""

    def test_display_mission_details_with_list_fields(self):
        """Mission display should format list fields correctly."""
        mission = {
            "project_name": "Test Project",
            "project_description": "A test",
            "tech_stack": ["docker", "k8s"],
            "scope": ["feature1", "feature2"],
            "estimated_hours": 40,
        }

        with patch("src.lms.steps.labs.console") as mock_console:
            display_mission_details(mission)
            mock_console.print.assert_called()

    def test_display_mission_details_with_string_fields(self):
        """Mission display should handle string tech_stack."""
        mission = {
            "project_name": "Test",
            "project_description": "Test",
            "tech_stack": "docker,k8s",
            "scope": "feature1,feature2",
            "estimated_hours": 40,
        }

        with patch("src.lms.steps.labs.console") as mock_console:
            display_mission_details(mission)
            mock_console.print.assert_called()


class TestMissionSaving:
    """Test mission saving functionality."""

    def test_save_mission_creates_file(self, tmp_path):
        """Saving mission should create JSON file in missions directory."""
        with patch("src.lms.steps.labs.get_missions_dir", return_value=tmp_path):
            mission = {
                "project_name": "Test",
                "project_description": "Test",
            }
            profile = {"level": "intermediate"}

            result = save_mission(mission, profile, "devops_engineer")

            assert result is True
            assert len(list(tmp_path.glob("mission_*.json"))) == 1

    def test_save_mission_contains_metadata(self, tmp_path):
        """Saved mission should include metadata."""
        with patch("src.lms.steps.labs.get_missions_dir", return_value=tmp_path):
            mission = {"project_name": "Test"}
            profile = {"level": "intermediate"}

            save_mission(mission, profile, "sre")

            # Read saved file
            mission_file = list(tmp_path.glob("mission_*.json"))[0]
            content = json.loads(mission_file.read_text())

            assert "created_at" in content
            assert content["role"] == "sre"
            assert content["learner_level"] == "intermediate"
            assert content["status"] == "active"

    def test_save_mission_exception_handling(self, tmp_path):
        """Save mission should return False on exception."""
        with patch(
            "src.lms.steps.labs.get_missions_dir",
            side_effect=Exception("Test error"),
        ):
            mission = {"project_name": "Test"}
            profile = {"level": "intermediate"}

            with patch("src.lms.steps.labs.console"):
                result = save_mission(mission, profile, "backend_engineer")

            assert result is False


class TestMissionEvaluation:
    """Test mission evaluation functionality."""

    @patch("src.lms.steps.labs.MissionEvaluator")
    @patch("src.lms.steps.labs.Confirm")
    @patch("src.lms.steps.labs.Prompt")
    def test_evaluate_mission_user_cancels(
        self, mock_prompt, mock_confirm, mock_evaluator_class
    ):
        """Evaluation should be skipped if user not ready."""
        mock_confirm.ask.return_value = False

        profile = {"level": "intermediate"}
        mission = {"project_name": "Test"}

        with patch("src.lms.steps.labs.console"):
            result = evaluate_mission(profile, "sre", mission)

        assert result is False

    @patch("src.lms.steps.labs.MissionEvaluator")
    @patch("src.lms.steps.labs.Confirm")
    @patch("src.lms.steps.labs.Prompt")
    def test_evaluate_mission_success(
        self, mock_prompt, mock_confirm, mock_evaluator_class
    ):
        """Successful evaluation should return True."""
        mock_confirm.ask.return_value = True
        mock_prompt.ask.return_value = str(Path.home() / "labs")

        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator

        evaluation_result = {
            "score": 85.0,
            "categories": {
                "completeness": 85.0,
                "code_quality": 85.0,
                "testing": 80.0,
                "devops": 90.0,
                "documentation": 85.0,
            },
            "feedback": "Great work!",
        }
        mock_evaluator.evaluate_project.return_value = evaluation_result

        profile = {"level": "intermediate"}
        mission = {"project_name": "Test"}

        with patch("src.lms.steps.labs.console"):
            result = evaluate_mission(profile, "devops_engineer", mission)

        assert result is True

    @patch("src.lms.steps.labs.MissionEvaluator")
    @patch("src.lms.steps.labs.Confirm")
    @patch("src.lms.steps.labs.Prompt")
    def test_evaluate_mission_failure(
        self, mock_prompt, mock_confirm, mock_evaluator_class
    ):
        """Failed evaluation should return False."""
        mock_confirm.ask.return_value = True
        mock_prompt.ask.return_value = str(Path.home() / "labs")

        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        mock_evaluator.evaluate_project.return_value = None

        profile = {"level": "junior"}
        mission = {"project_name": "Test"}

        with patch("src.lms.steps.labs.console"):
            result = evaluate_mission(profile, "sre", mission)

        assert result is False


class TestProgressionAwards:
    """Test role progression and star awards."""

    def test_award_progression_below_threshold(self):
        """No stars awarded if score below 70."""
        result = award_progression("junior", 65.0, "sre")
        assert result is None

    def test_award_progression_one_star(self):
        """One star awarded for score 70-79."""
        result = award_progression("junior", 75.0, "cloud_engineer")
        assert result is not None
        assert "⭐" in result["stars"]
        assert "Cloud Engineer" in result["new_title"]

    def test_award_progression_two_stars(self):
        """Two stars awarded for score 80-89 (formula: int((score-70)/10))."""
        result = award_progression("intermediate", 89.0, "devops_engineer")
        assert result is not None
        assert result["stars"].count("⭐") == 1  # 89: (89-70)/10 = 1.9 -> 1 star

    def test_award_progression_three_stars(self):
        """Multiple stars awarded for high scores (formula: int((score-70)/10))."""
        result = award_progression("senior", 100.0, "sre")
        assert result is not None
        assert result["stars"].count("⭐") == 3  # 100: (100-70)/10 = 3.0 -> 3 stars
        assert "Sre" in result["new_title"]

    def test_award_progression_perfect_score(self):
        """Perfect score should award max stars."""
        result = award_progression("senior", 100.0, "infrastructure_engineer")
        assert result is not None
        assert result["score"] == 100.0
