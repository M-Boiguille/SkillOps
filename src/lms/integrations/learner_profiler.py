"""Learner profile analysis and level determination."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path
import json
from enum import Enum

from rich.console import Console

console = Console()


class LearnerLevel(str, Enum):
    """Learner proficiency levels."""

    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"


@dataclass
class SkillAssessment:
    """Assessment of a specific skill."""

    skill_name: str
    score: int  # 0-100
    hours_practice: int
    last_used_date: Optional[str]
    confidence: str  # "low", "medium", "high"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class LearnerProfile:
    """Complete learner profile with progression tracking."""

    username: str
    current_level: LearnerLevel
    overall_score: int  # 0-100
    completed_missions: int
    skills: list[SkillAssessment]
    learning_gaps: list[str]
    missions_by_role: dict[str, list[str]]  # role -> [mission_ids]
    last_evaluation_date: Optional[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "username": self.username,
            "current_level": self.current_level.value,
            "overall_score": self.overall_score,
            "completed_missions": self.completed_missions,
            "skills": [s.to_dict() for s in self.skills],
            "learning_gaps": self.learning_gaps,
            "missions_by_role": self.missions_by_role,
            "last_evaluation_date": self.last_evaluation_date,
        }


class LearnerProfiler:
    """Analyzes learner progression and determines readiness for missions."""

    # Scoring thresholds
    LEVEL_THRESHOLDS = {
        "junior": (0, 40),
        "intermediate": (41, 75),
        "senior": (76, 100),
    }

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize profiler.

        Args:
            storage_path: Path to store learner profiles. Defaults to .skillops/profiles/
        """
        self.storage_path = (
            Path(storage_path)
            if storage_path
            else Path.home() / ".skillops" / "profiles"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def evaluate_learner_level(
        self,
        reinforce_stats: dict,
        anki_stats: dict,
        github_activity: dict,
        self_assessment: Optional[dict] = None,
    ) -> LearnerProfile:
        """Evaluate learner level from multiple sources.

        Args:
            reinforce_stats: Stats from REINFORCE step
            anki_stats: Stats from Anki integration
            github_activity: Activity from GitHub
            self_assessment: Optional self-assessment scores

        Returns:
            LearnerProfile with calculated level and scores
        """
        # Calculate component scores (0-100 each)
        reinforce_score = self._calculate_reinforce_score(reinforce_stats)
        anki_score = self._calculate_anki_score(anki_stats)
        github_score = self._calculate_github_score(github_activity)
        self_score = self_assessment.get("score", 50) if self_assessment else 50

        # Weighted average (reinforce=35%, anki=25%, github=20%, self=20%)
        overall_score = int(
            (reinforce_score * 0.35)
            + (anki_score * 0.25)
            + (github_score * 0.20)
            + (self_score * 0.20)
        )

        # Determine level
        level = self._score_to_level(overall_score)

        # Extract skills from sources
        skills = self._extract_skills(reinforce_stats, anki_stats, github_activity)

        # Identify learning gaps
        learning_gaps = self._identify_gaps(reinforce_stats, skills)

        # Create profile
        profile = LearnerProfile(
            username=github_activity.get("username", "unknown"),
            current_level=level,
            overall_score=overall_score,
            completed_missions=reinforce_stats.get("completed_exercises", 0),
            skills=skills,
            learning_gaps=learning_gaps,
            missions_by_role={},
            last_evaluation_date=None,
        )

        return profile

    def _calculate_reinforce_score(self, stats: dict) -> int:
        """Calculate score from REINFORCE statistics."""
        if not stats:
            return 50

        completed = stats.get("completed_exercises", 0)
        total = stats.get("total_exercises", 1)
        completion_rate = min(100, (completed / total * 100)) if total > 0 else 0

        accuracy = stats.get("average_accuracy", 50)

        # 60% completion, 40% accuracy
        score = int((completion_rate * 0.6) + (accuracy * 0.4))
        return min(100, score)

    def _calculate_anki_score(self, stats: dict) -> int:
        """Calculate score from Anki statistics."""
        if not stats:
            return 50

        # Use retention rate as primary metric
        retention = stats.get("retention_rate", 50)
        deck_count = stats.get("decks", 0)

        # Bonus for multiple decks (shows breadth)
        deck_bonus = min(20, deck_count * 2)

        score = int(retention + (deck_bonus * 0.2))
        return min(100, score)

    def _calculate_github_score(self, stats: dict) -> int:
        """Calculate score from GitHub activity."""
        if not stats:
            return 50

        commits_per_week = stats.get("commits_per_week", 0)
        repos_contributed = stats.get("repos_contributed", 0)
        stars_received = stats.get("stars_received", 0)

        # Normalize metrics
        commit_score = min(50, commits_per_week * 5)
        repo_score = min(30, repos_contributed * 3)
        star_score = min(20, stars_received * 2)

        score = int(commit_score + repo_score + star_score) // 10
        return min(100, score)

    def _score_to_level(self, score: int) -> LearnerLevel:
        """Convert numeric score to proficiency level."""
        if score <= 40:
            return LearnerLevel.JUNIOR
        elif score <= 75:
            return LearnerLevel.INTERMEDIATE
        else:
            return LearnerLevel.SENIOR

    def _extract_skills(
        self, reinforce_stats: dict, anki_stats: dict, github_stats: dict
    ) -> list[SkillAssessment]:
        """Extract detected skills from sources."""
        skills = {}

        # From REINFORCE (exercise topics)
        if reinforce_stats and "exercise_topics" in reinforce_stats:
            for topic, count in reinforce_stats["exercise_topics"].items():
                score = min(100, count * 10)
                skills[topic] = SkillAssessment(
                    skill_name=topic,
                    score=score,
                    hours_practice=count * 2,
                    last_used_date=reinforce_stats.get("last_exercise_date"),
                    confidence="medium",
                )

        # From Anki (deck names as topics)
        if anki_stats and "deck_names" in anki_stats:
            for deck in anki_stats["deck_names"]:
                if deck not in skills:
                    skills[deck] = SkillAssessment(
                        skill_name=deck,
                        score=anki_stats.get("retention_rate", 50),
                        hours_practice=10,
                        last_used_date=anki_stats.get("last_review_date"),
                        confidence="high",
                    )

        # From GitHub (detected from repo languages)
        if github_stats and "languages" in github_stats:
            for lang in github_stats["languages"]:
                if lang not in skills:
                    skills[lang] = SkillAssessment(
                        skill_name=lang,
                        score=70,
                        hours_practice=20,
                        last_used_date=github_stats.get("last_commit_date"),
                        confidence="high",
                    )

        return list(skills.values())

    def _identify_gaps(
        self, reinforce_stats: dict, skills: list[SkillAssessment]
    ) -> list[str]:
        """Identify skill gaps for learning recommendations."""
        gaps = []

        # Common DevOps skills to check
        expected_skills = {
            "Python",
            "Bash",
            "Docker",
            "Kubernetes",
            "Terraform",
            "CI/CD",
            "Monitoring",
            "Git",
        }

        existing_skills = {s.skill_name for s in skills}
        missing = expected_skills - existing_skills

        # Identify weak skills (score < 60)
        weak_skills = {s.skill_name for s in skills if s.score < 60}

        gaps.extend(list(missing)[:3])  # Top 3 missing
        gaps.extend(list(weak_skills)[:2])  # Top 2 weak

        return gaps

    def save_profile(self, profile: LearnerProfile) -> bool:
        """Save learner profile to disk.

        Args:
            profile: LearnerProfile to save

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.storage_path / f"{profile.username}.json"
            with open(filepath, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)
            return True
        except (IOError, OSError) as e:
            console.print(f"[red]Error saving profile: {e}[/red]")
            return False

    def load_profile(self, username: str) -> Optional[LearnerProfile]:
        """Load learner profile from disk.

        Args:
            username: Username to load

        Returns:
            LearnerProfile if found, None otherwise
        """
        try:
            filepath = self.storage_path / f"{username}.json"
            if not filepath.exists():
                return None

            with open(filepath, "r") as f:
                data = json.load(f)

            # Reconstruct profile
            skills = [
                SkillAssessment(
                    skill_name=s["skill_name"],
                    score=s["score"],
                    hours_practice=s["hours_practice"],
                    last_used_date=s["last_used_date"],
                    confidence=s["confidence"],
                )
                for s in data["skills"]
            ]

            profile = LearnerProfile(
                username=data["username"],
                current_level=LearnerLevel(data["current_level"]),
                overall_score=data["overall_score"],
                completed_missions=data["completed_missions"],
                skills=skills,
                learning_gaps=data["learning_gaps"],
                missions_by_role=data["missions_by_role"],
                last_evaluation_date=data["last_evaluation_date"],
            )

            return profile
        except (IOError, OSError, json.JSONDecodeError, KeyError) as e:
            console.print(f"[red]Error loading profile: {e}[/red]")
            return None

    def is_ready_for_mission(
        self,
        profile: LearnerProfile,
        mission_required_skills: list[str],
        threshold: int = 60,
    ) -> tuple[bool, list[str]]:
        """Check if learner is ready for mission.

        Args:
            profile: Learner profile
            mission_required_skills: Skills required for mission
            threshold: Minimum skill score to be "ready"

        Returns:
            (is_ready, missing_or_weak_skills)
        """
        issues = []
        existing_skills = {s.skill_name: s.score for s in profile.skills}

        for skill in mission_required_skills:
            if skill not in existing_skills:
                issues.append(f"Missing: {skill}")
            elif existing_skills[skill] < threshold:
                issues.append(
                    f"Weak: {skill} ({existing_skills[skill]}/100) - need {threshold}+"
                )

        is_ready = len(issues) == 0
        return is_ready, issues

    def get_role_progression(
        self, profile: LearnerProfile, role: str
    ) -> tuple[str, int]:
        """Get learner's progression in a specific role.

        Returns:
            (progression_level, star_count)
            Examples: ("Junior", 2), ("Intermediate", 4), ("Senior", 5)
        """
        missions_count = len(profile.missions_by_role.get(role, []))

        # Progression logic
        if missions_count == 0:
            return ("Beginner", 0)
        elif missions_count == 1:
            return ("Junior", 2)
        elif missions_count == 2:
            return ("Junior", 3)
        elif missions_count == 3:
            return ("Intermediate", 3)
        elif missions_count == 4:
            return ("Intermediate", 4)
        elif missions_count == 5:
            return ("Senior", 4)
        else:
            return ("Senior", 5)
