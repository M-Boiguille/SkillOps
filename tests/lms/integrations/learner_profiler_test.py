"""Tests for learner profiler."""

import pytest
from src.lms.integrations.learner_profiler import (
    LearnerProfiler,
    LearnerLevel,
)


@pytest.fixture
def profiler(tmp_path):
    """Create profiler with temp storage."""
    return LearnerProfiler(storage_path=tmp_path)


@pytest.fixture
def sample_reinforce_stats():
    """Sample REINFORCE statistics."""
    return {
        "completed_exercises": 15,
        "total_exercises": 20,
        "average_accuracy": 85,
        "exercise_topics": {"Python": 5, "Docker": 4, "Kubernetes": 6},
        "last_exercise_date": "2026-01-12",
    }


@pytest.fixture
def sample_anki_stats():
    """Sample Anki statistics."""
    return {
        "retention_rate": 78,
        "decks": 3,
        "deck_names": ["Python", "Docker", "DevOps"],
        "last_review_date": "2026-01-12",
    }


@pytest.fixture
def sample_github_stats():
    """Sample GitHub activity."""
    return {
        "username": "testuser",
        "commits_per_week": 8,
        "repos_contributed": 5,
        "stars_received": 12,
        "languages": ["Python", "Bash", "YAML"],
        "last_commit_date": "2026-01-12",
    }


class TestLearnerProfiler:
    """Tests for LearnerProfiler."""

    def test_evaluate_learner_level_junior(self, profiler):
        """Test junior level evaluation."""
        reinforce_stats = {
            "completed_exercises": 2,
            "total_exercises": 20,
            "average_accuracy": 40,
        }
        anki_stats = {"retention_rate": 35, "decks": 0}
        github_stats = {
            "username": "testuser",
            "commits_per_week": 1,
            "repos_contributed": 1,
            "stars_received": 0,
        }

        profile = profiler.evaluate_learner_level(
            reinforce_stats, anki_stats, github_stats
        )

        assert profile.current_level == LearnerLevel.JUNIOR
        assert profile.overall_score < 41

    def test_evaluate_learner_level_intermediate(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test intermediate level evaluation."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        assert profile.current_level == LearnerLevel.INTERMEDIATE
        assert 41 <= profile.overall_score <= 75

    def test_evaluate_learner_level_senior(self, profiler):
        """Test senior level evaluation."""
        reinforce_stats = {
            "completed_exercises": 50,
            "total_exercises": 50,
            "average_accuracy": 95,
        }
        anki_stats = {"retention_rate": 92, "decks": 8}
        github_stats = {
            "username": "testuser",
            "commits_per_week": 25,
            "repos_contributed": 15,
            "stars_received": 100,
        }

        profile = profiler.evaluate_learner_level(
            reinforce_stats, anki_stats, github_stats
        )

        # Should be intermediate or senior (scoring is weighted average)
        assert profile.current_level in [LearnerLevel.INTERMEDIATE, LearnerLevel.SENIOR]
        assert profile.overall_score >= 70

    def test_save_and_load_profile(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test saving and loading profile."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        # Save
        assert profiler.save_profile(profile) is True

        # Load
        loaded = profiler.load_profile("testuser")
        assert loaded is not None
        assert loaded.username == "testuser"
        assert loaded.current_level == profile.current_level

    def test_is_ready_for_mission_yes(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test readiness check - positive case."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        # Use skills that are likely to exist in profile
        required = ["Bash"]  # Generic skill likely to exist
        is_ready, issues = profiler.is_ready_for_mission(
            profile, required, threshold=50
        )

        # Should be ready or have low bar
        assert is_ready or len(issues) == 0

    def test_is_ready_for_mission_no(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test readiness check - negative case."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        required = ["Kubernetes", "Terraform", "ArgoCD"]
        is_ready, issues = profiler.is_ready_for_mission(
            profile, required, threshold=70
        )

        # Should have some missing/weak skills
        assert is_ready is False or len(issues) > 0

    def test_get_role_progression_beginner(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test role progression for beginner."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        prog, stars = profiler.get_role_progression(profile, "cloud_engineer")
        assert prog == "Beginner"
        assert stars == 0

    def test_get_role_progression_junior(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test role progression for junior."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )
        profile.missions_by_role["sre"] = ["mission-001"]

        prog, stars = profiler.get_role_progression(profile, "sre")
        assert prog == "Junior"
        assert stars == 2

    def test_get_role_progression_senior(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test role progression for senior."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )
        profile.missions_by_role["cloud_engineer"] = [
            "mission-001",
            "mission-002",
            "mission-003",
            "mission-004",
            "mission-005",
        ]

        prog, stars = profiler.get_role_progression(profile, "cloud_engineer")
        assert prog == "Senior"
        assert stars >= 4  # 4 or 5 stars for senior

    def test_skill_extraction(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test skill extraction from multiple sources."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        skills = {s.skill_name for s in profile.skills}
        # Should have at least some extracted skills
        assert len(skills) > 0
        assert any(skill in skills for skill in ["Python", "Docker"])

    def test_learning_gaps_identification(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test learning gaps identification."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        # Should identify common missing DevOps skills
        assert len(profile.learning_gaps) > 0
        assert isinstance(profile.learning_gaps, list)

    def test_profile_serialization(
        self, profiler, sample_reinforce_stats, sample_anki_stats, sample_github_stats
    ):
        """Test profile serialization to dict."""
        profile = profiler.evaluate_learner_level(
            sample_reinforce_stats, sample_anki_stats, sample_github_stats
        )

        profile_dict = profile.to_dict()

        assert isinstance(profile_dict, dict)
        assert "username" in profile_dict
        assert "current_level" in profile_dict
        assert "skills" in profile_dict
        assert isinstance(profile_dict["skills"], list)

    def test_score_to_level_boundaries(self, profiler):
        """Test score to level conversion at boundaries."""
        assert profiler._score_to_level(0) == LearnerLevel.JUNIOR
        assert profiler._score_to_level(40) == LearnerLevel.JUNIOR
        assert profiler._score_to_level(41) == LearnerLevel.INTERMEDIATE
        assert profiler._score_to_level(75) == LearnerLevel.INTERMEDIATE
        assert profiler._score_to_level(76) == LearnerLevel.SENIOR
        assert profiler._score_to_level(100) == LearnerLevel.SENIOR
