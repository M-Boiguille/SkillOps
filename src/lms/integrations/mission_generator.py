"""Mission generation using Gemini AI."""

from __future__ import annotations

import os
from typing import Optional
import json

from google import genai
from rich.console import Console

console = Console()


class MissionGenerator:
    """Generate realistic DevOps mission briefs using Gemini AI."""

    # Predefined roles and their characteristics
    ROLES = {
        "cloud_engineer": {
            "title": "Cloud Engineer",
            "description": "Build and manage cloud infrastructure",
            "tech_stacks": [
                "AWS/Terraform",
                "GCP/Deployment Manager",
                "Azure/ARM templates",
            ],
        },
        "sre": {
            "title": "Site Reliability Engineer",
            "description": "Build observability, reliability, and automation",
            "tech_stacks": [
                "Prometheus/Grafana",
                "ELK Stack",
                "Datadog",
            ],
        },
        "cicd_specialist": {
            "title": "CI/CD Specialist",
            "description": "Design and maintain deployment pipelines",
            "tech_stacks": [
                "GitHub Actions",
                "GitLab CI",
                "Jenkins",
            ],
        },
        "backend_engineer": {
            "title": "Backend Engineer",
            "description": "Build scalable APIs and services",
            "tech_stacks": [
                "Python/FastAPI",
                "Node.js/Express",
                "Go/Gin",
            ],
        },
        "devops_engineer": {
            "title": "DevOps Engineer",
            "description": "Automate infrastructure and deployment",
            "tech_stacks": [
                "Kubernetes/Helm",
                "Docker",
                "Ansible",
            ],
        },
        "infrastructure_engineer": {
            "title": "Infrastructure Engineer",
            "description": "Design and implement infrastructure",
            "tech_stacks": [
                "Terraform",
                "CloudFormation",
                "Packer",
            ],
        },
    }

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
        # - 1M token context for understanding learner profiles
        # - Hybrid reasoning for adaptive mission generation
        # - 100% free (input + output)

    def generate_mission(
        self,
        role: str,
        learner_level: str,
        learner_skills: list[str],
        mode: str = "ai_suggested",
        user_idea: Optional[str] = None,
    ) -> dict:
        """Generate a complete mission specification.

        Args:
            role: Role to generate mission for (from ROLES.keys())
            learner_level: "junior", "intermediate", or "senior"
            learner_skills: List of skills learner already has
            mode: "ai_suggested" or "po_mode" (product owner idea)
            user_idea: If mode="po_mode", the user's project idea

        Returns:
            Mission specification dict
        """
        if role not in self.ROLES:
            raise ValueError(
                f"Unknown role: {role}. Available: {list(self.ROLES.keys())}"
            )

        role_info = self.ROLES[role]

        # Build prompt based on mode
        if mode == "po_mode" and user_idea:
            prompt = self._build_po_prompt(
                role, learner_level, learner_skills, user_idea
            )
        else:
            prompt = self._build_ai_suggested_prompt(
                role, role_info, learner_level, learner_skills
            )

        # Call Gemini
        response = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        if not response.text:
            raise ValueError("Failed to generate mission from Gemini")

        # Parse response
        mission_spec = self._parse_mission_response(response.text)
        mission_spec["role"] = role
        mission_spec["mode"] = mode
        mission_spec["learner_level"] = learner_level

        return mission_spec

    def _build_ai_suggested_prompt(
        self, role: str, role_info: dict, learner_level: str, skills: list[str]
    ) -> str:
        """Build prompt for AI-suggested mission."""
        return f"""
You are an expert technical curriculum designer. Generate a complete DevOps mission brief.

CONTEXT:
- Role: {role_info['title']}
- Learner Level: {learner_level.upper()}
- Current Skills: {', '.join(skills) if skills else 'None yet'}
- Goal: Build a complete, production-ready project (not a fragment)

REQUIREMENTS:
1. Project Name: Should be realistic and achievable
2. Project Description: 2-3 sentences explaining the business need
3. Tech Stack: Based on role, list 3-5 technologies to use
4. Scope: Outline major features/components
5. Learning Path:
   - If learner missing skills: Suggest 2-3 skills to learn
   - If learner has gaps: Recommend specific learning resources
6. MVP Features: Core features that are achievable (60% of time)
7. Excellence Features: Stretch goals for advanced learning
8. Success Criteria: How to measure if project is successful
9. Estimated Duration: Total hours to complete

RESPONSE FORMAT:
Return ONLY JSON (no markdown, no explanation):
{{"project_name": "...", "project_description": "...", "tech_stack": [],
"scope": [], "learning_needs": [], "mvp_features": [], "excellence_features": [],
"success_criteria": [], "estimated_hours": 40}}
"""

    def _build_po_prompt(
        self,
        role: str,
        learner_level: str,
        skills: list[str],
        user_idea: str,
    ) -> str:
        """Build prompt for Product Owner mode."""
        return f"""
You are an expert DevOps architect. Transform a user's idea into a technical mission.

CONTEXT:
- Role: {role.replace('_', ' ').title()}
- Learner Level: {learner_level.upper()}
- Current Skills: {', '.join(skills) if skills else 'None yet'}
- User's Idea: {user_idea}

TASK:
Transform the user's idea into a production-ready DevOps project. Recommend learning first.

RESPONSE FORMAT:
Return ONLY JSON (no markdown, no explanation):
{{"project_name": "...", "project_description": "...", "tech_stack": [],
"scope": [], "learning_needs": [], "mvp_features": [], "excellence_features": [],
"success_criteria": [], "estimated_hours": 40}}
"""

    def _parse_mission_response(self, response_text: str) -> dict:
        """Parse Gemini response into mission dict."""
        try:
            # Try to extract JSON from response
            json_str = response_text.strip()
            if json_str.startswith("```"):
                # Remove markdown code blocks if present
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            json_str = json_str.strip()

            mission = json.loads(json_str)
            return mission
        except (json.JSONDecodeError, IndexError, ValueError) as e:
            console.print(f"[red]Failed to parse Gemini response: {e}[/red]")
            # Return default mission structure on parse error
            return {
                "project_name": "Default Project",
                "project_description": response_text[:200],
                "tech_stack": ["Python", "Docker"],
                "scope": ["Setup", "Implementation", "Testing"],
                "learning_needs": [],
                "mvp_features": ["Core feature"],
                "excellence_features": [],
                "success_criteria": ["Tests pass", "Documented"],
                "estimated_hours": 20,
            }

    def validate_mission_feasibility(
        self, mission: dict, learner_skills: list[str]
    ) -> tuple[bool, list[str]]:
        """Validate if mission is feasible with learner's skills.

        Returns:
            (is_feasible, missing_skills)
        """
        learning_needs = mission.get("learning_needs", [])
        missing_skills = []

        # Check if too many missing skills
        for need in learning_needs:
            if need.get("priority") == "high":
                missing_skills.append(need["skill"])

        # Feasible if <= 3 high priority learning needs
        is_feasible = len(missing_skills) <= 3

        return is_feasible, missing_skills

    @staticmethod
    def get_available_roles() -> dict:
        """Return all available roles."""
        return MissionGenerator.ROLES
