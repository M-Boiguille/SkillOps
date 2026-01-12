"""Mission evaluation using Gemini AI."""

from __future__ import annotations

import os
import json
from typing import Optional
from pathlib import Path

from google import genai
from rich.console import Console

console = Console()


class MissionEvaluator:
    """Evaluate completed DevOps projects using Gemini AI."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini AI client.

        Args:
            api_key: Google API key. Defaults to GEMINI_API_KEY env var
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=self.api_key)
        # Using gemini-2.5-flash: best balance of speed, quality, and cost
        # - 1M token context for detailed code/project evaluation
        # - Hybrid reasoning for constructive feedback generation
        # - 100% free (input + output)

    def evaluate_project(
        self,
        project_path: str,
        mission_spec: dict,
        learner_level: str,
    ) -> dict:
        """Evaluate a completed project against mission requirements.

        Args:
            project_path: Path to project directory
            mission_spec: Original mission specification
            learner_level: Learner's current level

        Returns:
            Evaluation result dict with score and feedback
        """
        # Collect project information
        project_info = self._collect_project_info(project_path)

        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            mission_spec, project_info, learner_level
        )

        # Call Gemini for evaluation
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response.text:
            raise ValueError("Failed to get evaluation from Gemini")

        # Parse evaluation response
        evaluation = self._parse_evaluation_response(response.text)

        return evaluation

    def _collect_project_info(self, project_path: str) -> dict:
        """Collect information about project structure and quality."""
        from pathlib import Path

        project = Path(project_path)
        if not project.exists():
            return {"error": f"Project path not found: {project_path}"}

        info = {
            "path": str(project),
            "has_readme": (project / "README.md").exists(),
            "has_dockerfile": (project / "Dockerfile").exists(),
            "has_ci_cd": (project / ".github" / "workflows").exists(),
            "has_tests": (project / "tests").exists(),
            "has_git": (project / ".git").exists(),
            "files": self._analyze_file_structure(project),
            "code_stats": self._analyze_code_stats(project),
        }

        return info

    def _analyze_file_structure(self, project_path: Path) -> dict:
        """Analyze project file structure."""
        file_types: dict[str, int] = {}
        for file in project_path.rglob("*"):
            if file.is_file() and not str(file).startswith("."):
                ext = file.suffix or "no_extension"
                file_types[ext] = file_types.get(ext, 0) + 1

        return file_types

    def _analyze_code_stats(self, project_path: Path) -> dict:
        """Basic code statistics."""
        total_lines = 0
        test_files = 0
        config_files = 0

        for file in project_path.rglob("*"):
            if file.is_file():
                if "test" in file.name:
                    test_files += 1
                if file.name in [
                    "docker-compose.yml",
                    "Dockerfile",
                    "pyproject.toml",
                    "package.json",
                ]:
                    config_files += 1
                try:
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        total_lines += len(f.readlines())
                except OSError:
                    pass

        return {
            "total_lines": total_lines,
            "test_files": test_files,
            "config_files": config_files,
        }

    def _build_evaluation_prompt(
        self, mission_spec: dict, project_info: dict, learner_level: str
    ) -> str:
        """Build evaluation prompt for Gemini."""
        return f"""
You are a senior DevOps architect evaluating a junior engineer's project submission.

MISSION BRIEF:
- Project Name: {mission_spec.get('project_name', 'Unknown')}
- Description: {mission_spec.get('project_description', '')}
- Required Tech: {', '.join(mission_spec.get('tech_stack', []))}
- MVP Features: {', '.join(mission_spec.get('mvp_features', []))}
- Success Criteria: {', '.join(mission_spec.get('success_criteria', []))}

SUBMITTED PROJECT:
- Has README: {project_info.get('has_readme', False)}
- Has Dockerfile: {project_info.get('has_dockerfile', False)}
- Has CI/CD: {project_info.get('has_ci_cd', False)}
- Has Tests: {project_info.get('has_tests', False)}
- Has Git: {project_info.get('has_git', False)}
- Total Lines of Code: {project_info.get('code_stats', {}).get('total_lines', 0)}
- Test Files: {project_info.get('code_stats', {}).get('test_files', 0)}
- Config Files: {project_info.get('code_stats', {}).get('config_files', 0)}

LEARNER LEVEL: {learner_level.upper()}

EVALUATION CRITERIA (100 points total):
1. Completeness (20 pts): All MVP features implemented?
2. Code Quality (25 pts): Structure, naming, documentation?
3. Testing (20 pts): Tests present and meaningful (>80% coverage)?
4. DevOps Practices (20 pts): CI/CD, Docker, IaC, monitoring?
5. Documentation (15 pts): README, comments, architecture docs?

RESPONSE FORMAT:
Return ONLY a JSON object (no markdown, no explanation):
{{
    "overall_score": 85,
    "level_achieved": "intermediate",
    "stars": 4,
    "scores": {{
        "completeness": 18,
        "code_quality": 20,
        "testing": 17,
        "devops_practices": 18,
        "documentation": 12
    }},
    "strengths": ["...", "..."],
    "improvements": ["...", "..."],
    "feedback": "...",
    "next_steps": ["...", "..."]
}}
"""

    def _parse_evaluation_response(self, response_text: str) -> dict:
        """Parse Gemini evaluation response."""
        try:
            json_str = response_text.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            json_str = json_str.strip()

            evaluation = json.loads(json_str)

            # Ensure all required fields
            defaults = {
                "overall_score": 0,
                "level_achieved": "junior",
                "stars": 1,
                "scores": {},
                "strengths": [],
                "improvements": [],
                "feedback": "",
                "next_steps": [],
            }

            return {**defaults, **evaluation}
        except (json.JSONDecodeError, IndexError, ValueError) as e:
            console.print(f"[red]Failed to parse evaluation: {e}[/red]")
            return {
                "overall_score": 50,
                "level_achieved": "junior",
                "stars": 2,
                "scores": {},
                "strengths": ["Project submitted"],
                "improvements": ["Review evaluation prompt"],
                "feedback": "Evaluation parsing failed",
                "next_steps": ["Resubmit"],
            }

    @staticmethod
    def calculate_level_from_score(score: int) -> str:
        """Convert numeric score to proficiency level."""
        if score <= 40:
            return "junior"
        elif score <= 75:
            return "intermediate"
        else:
            return "senior"

    @staticmethod
    def calculate_stars(score: int) -> int:
        """Convert score to star rating (1-5)."""
        if score <= 20:
            return 1
        elif score <= 40:
            return 2
        elif score <= 60:
            return 3
        elif score <= 80:
            return 4
        else:
            return 5
