"""Labs step - AI-powered mission system for portfolio building.

This step implements the "Labs Fictive" feature, integrating learner profiling,
AI-generated mission creation, and automatic evaluation into a seamless workflow
that builds your DevOps portfolio with role-based progression.

Workflow:
  1. Profile Learner: Analyze REINFORCE/Anki/GitHub stats -> determine level
  2. Suggest/Select: AI recommends missions OR Product Owner provides ideas
  3. Execute: You work on the mission (real DevOps project)
  4. Evaluate: System scores your project and awards role progression stars
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.lms.integrations.learner_profiler import (
    LearnerProfiler,
    LearnerLevel,
)
from src.lms.integrations.mission_generator import MissionGenerator
from src.lms.integrations.mission_evaluator import MissionEvaluator
from src.lms.display import (
    display_error_message,
    display_info_panel,
    display_section_header,
    display_success_message,
)

console = Console()

# Available DevOps roles for mission selection
AVAILABLE_ROLES = [
    "cloud_engineer",
    "sre",
    "cicd_specialist",
    "backend_engineer",
    "devops_engineer",
    "infrastructure_engineer",
]


def get_storage_path() -> Path:
    """Get the storage path for missions and profiles.

    Returns:
        Absolute path to storage directory.
    """
    storage_path_str = os.getenv(
        "STORAGE_PATH", str(Path.home() / ".local/share/skillops")
    )
    return Path(storage_path_str).expanduser().absolute()


def get_missions_dir() -> Path:
    """Get the missions storage directory.

    Returns:
        Absolute path to .skillops/missions/
    """
    missions_dir = Path.home() / ".skillops" / "missions"
    missions_dir.mkdir(parents=True, exist_ok=True)
    return missions_dir


def get_profiles_dir() -> Path:
    """Get the profiles storage directory.

    Returns:
        Absolute path to ~/.skillops/profiles/
    """
    profiles_dir = Path.home() / ".skillops" / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def display_mission_header() -> None:
    """Display the Labs Fictive header."""
    header_text = Text("Labs Fictive", style="bold magenta", justify="center")
    subtitle = Text(
        "AI-Powered DevOps Missions for Portfolio Building",
        style="dim",
        justify="center",
    )

    panel = Panel(
        f"{header_text}\n{subtitle}",
        title="🎯 Mission Mode",
        border_style="magenta",
        padding=(1, 2),
    )
    console.print(panel)


def profile_learner() -> Optional[dict]:
    """Profile the learner to determine their level and readiness.

    Analyzes REINFORCE exercises, Anki deck stats, and GitHub contributions
    to produce a weighted learner profile.

    Returns:
        Dictionary with learner profile data, or None if skipped.
    """
    display_section_header("Analyzing Your Learning Progress...")

    profiler = LearnerProfiler(
        storage_path=get_storage_path(),
        github_token=os.getenv("GITHUB_TOKEN"),
        github_username=os.getenv("GITHUB_USERNAME"),
    )

    try:
        profile = profiler.evaluate_learner_level()

        # Display profile
        table = Table(title="📊 Your Learning Profile", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Level", profile["level"].upper())
        table.add_row(
            "Overall Score", f"{profile['overall_score']:.1f}/100"
        )
        table.add_row("REINFORCE (35%)", f"{profile['reinforce_score']:.1f}/100")
        table.add_row("Anki (25%)", f"{profile['anki_score']:.1f}/100")
        table.add_row("GitHub (20%)", f"{profile['github_score']:.1f}/100")
        table.add_row("Self-Assessment (20%)", f"{profile['self_score']:.1f}/100")

        console.print(table)
        console.print()

        # Check readiness for missions
        is_ready = profiler.is_ready_for_mission(profile)
        if is_ready:
            display_success_message(
                "✅ You're ready for a mission! Let's build something amazing."
            )
        else:
            display_info_panel(
                "You're building foundational skills. "
                "Continue with REINFORCE and Anki before attempting a mission."
            )
            return None

        return profile

    except Exception as e:
        display_error_message(f"Failed to profile learner: {str(e)}")
        return None


def select_role() -> Optional[str]:
    """Let the user select their target DevOps role.

    Returns:
        The selected role string, or None if skipped.
    """
    display_section_header("Select Your DevOps Role")

    role_descriptions = {
        "cloud_engineer": "☁️  Cloud Engineer - AWS/Azure/GCP expertise",
        "sre": "🔧 SRE (Site Reliability Engineer) - Systems & reliability",
        "cicd_specialist": "🔄 CI/CD Specialist - Pipeline & automation",
        "backend_engineer": "🐍 Backend Engineer - Services & infrastructure",
        "devops_engineer": "⚙️  DevOps Engineer - Full stack automation",
        "infrastructure_engineer": "🏗️  Infrastructure Engineer - IaC & architecture",
    }

    console.print("Available roles:")
    for role in AVAILABLE_ROLES:
        console.print(f"  • {role_descriptions[role]}")
    console.print()

    selected = Prompt.ask(
        "Enter your role",
        choices=AVAILABLE_ROLES,
        default="devops_engineer",
    )
    return selected


def generate_or_suggest_mission(
    profile: dict, role: str
) -> Optional[dict]:
    """Generate a mission using Gemini AI or accept user's idea.

    Offers two modes:
      - AI-Suggested: System recommends a mission based on level and skills gap
      - Product Owner: User provides an idea, AI transforms it

    Args:
        profile: Learner profile from profiler
        role: Selected DevOps role

    Returns:
        Mission specification dict, or None if cancelled.
    """
    display_section_header("Create Your Mission")

    console.print("Two modes available:")
    console.print("  1️⃣  AI-Suggested: System recommends based on your level")
    console.print("  2️⃣  Product Owner: You provide an idea, AI transforms it")
    console.print()

    mode = Prompt.ask(
        "Choose mode", choices=["1", "2"], default="1"
    )

    generator = MissionGenerator(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    try:
        if mode == "1":
            # AI-Suggested mode
            console.print("[dim]Generating mission recommendation...[/dim]")
            mission = generator.generate_mission(
                role=role,
                learner_level=profile["level"],
                current_skills=[s.strip() for s in profile.get("skills", [])],
                user_idea=None,  # Let AI suggest
                mode="ai_suggested",
            )
        else:
            # Product Owner mode
            user_idea = Prompt.ask(
                "Describe your mission idea (what do you want to build?)"
            )
            if not user_idea.strip():
                display_error_message("Mission idea cannot be empty.")
                return None

            console.print("[dim]Transforming your idea into a mission...[/dim]")
            mission = generator.generate_mission(
                role=role,
                learner_level=profile["level"],
                current_skills=[s.strip() for s in profile.get("skills", [])],
                user_idea=user_idea,
                mode="po_mode",
            )

        if mission:
            # Display mission details
            display_mission_details(mission)
            return mission
        else:
            display_error_message("Failed to generate mission. Try again.")
            return None

    except Exception as e:
        display_error_message(f"Mission generation failed: {str(e)}")
        return None


def display_mission_details(mission: dict) -> None:
    """Display formatted mission details.

    Args:
        mission: Mission specification dict
    """
    table = Table(title="🎯 Your Mission", show_header=True)
    table.add_column("Field", style="cyan")
    table.add_column("Details", style="yellow")

    table.add_row("Project Name", mission.get("project_name", "N/A"))
    table.add_row("Description", mission.get("project_description", "N/A"))

    tech_stack = mission.get("tech_stack", [])
    if isinstance(tech_stack, list):
        table.add_row("Tech Stack", ", ".join(tech_stack))
    else:
        table.add_row("Tech Stack", str(tech_stack))

    scope = mission.get("scope", [])
    if isinstance(scope, list):
        table.add_row("Scope", "\n".join(f"  • {s}" for s in scope))
    else:
        table.add_row("Scope", str(scope))

    table.add_row(
        "Estimated Hours",
        str(mission.get("estimated_hours", "N/A")),
    )

    console.print(table)
    console.print()


def save_mission(mission: dict, profile: dict, role: str) -> bool:
    """Save mission to local storage for tracking.

    Args:
        mission: Mission specification
        profile: Learner profile
        role: Selected role

    Returns:
        True if saved successfully.
    """
    try:
        missions_dir = get_missions_dir()
        mission_file = missions_dir / f"mission_{int(datetime.now().timestamp())}.json"

        mission_record = {
            "created_at": datetime.now().isoformat(),
            "role": role,
            "learner_level": profile["level"],
            "mission": mission,
            "status": "active",  # active, completed, abandoned
        }

        mission_file.write_text(json.dumps(mission_record, indent=2))
        return True
    except Exception as e:
        console.print(f"[red]Failed to save mission: {str(e)}[/red]")
        return False


def evaluate_mission(profile: dict, role: str, mission: dict) -> bool:
    """Evaluate a completed mission project.

    After the user completes the project, the evaluator assesses it across
    multiple dimensions and awards role progression.

    Args:
        profile: Learner profile
        role: Role for the mission
        mission: Mission specification

    Returns:
        True if evaluation completed.
    """
    display_section_header("Mission Evaluation")

    ready = Confirm.ask(
        "Have you completed the mission project? "
        "(Ensure it's in ~/labs or provide the path)"
    )
    if not ready:
        console.print("[dim]Come back when you're ready![/dim]\n")
        return False

    project_path = Prompt.ask(
        "Path to your project", default=str(Path.home() / "labs")
    )

    evaluator = MissionEvaluator(api_key=os.getenv("GEMINI_API_KEY"))

    try:
        console.print("[dim]Evaluating your project...[/dim]")
        evaluation = evaluator.evaluate_project(
            project_path=project_path,
            mission_spec=mission,
            learner_level=profile["level"],
        )

        if evaluation:
            # Display evaluation results
            display_evaluation_results(evaluation)

            # Award progression stars
            role_progression = award_progression(
                profile["level"],
                evaluation["score"],
                role,
            )
            if role_progression:
                display_success_message(
                    f"⭐ {role_progression['stars']} "
                    f"{role_progression['new_title']}"
                )

            return True
        else:
            display_error_message(
                "Evaluation failed. Check project structure."
            )
            return False

    except Exception as e:
        display_error_message(f"Evaluation error: {str(e)}")
        return False


def display_evaluation_results(evaluation: dict) -> None:
    """Display formatted evaluation results.

    Args:
        evaluation: Evaluation results dict
    """
    table = Table(title="📋 Evaluation Results", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Score", style="green")

    table.add_row(
        "Overall Score", f"{evaluation['score']:.1f}/100"
    )
    if "categories" in evaluation:
        for category, score in evaluation["categories"].items():
            table.add_row(f"  • {category.title()}", f"{score:.1f}/100")

    console.print(table)

    if "feedback" in evaluation:
        console.print("\n[yellow]Feedback:[/yellow]")
        console.print(evaluation["feedback"])

    console.print()


def award_progression(
    current_level: str,
    score: float,
    role: str,
) -> Optional[dict]:
    """Award role progression stars based on evaluation score.

    Progression:
      - 70-79: 1 star (Learner)
      - 80-89: 2 stars (Practitioner)
      - 90+: 3+ stars (Expert)

    Args:
        current_level: Current learner level (junior/intermediate/senior)
        score: Evaluation score (0-100)
        role: Role name

    Returns:
        Dict with stars and new title, or None if no progression.
    """
    stars = max(1, int((score - 70) / 10)) if score >= 70 else 0

    if stars == 0:
        return None

    # Build role title with stars
    role_title = role.replace("_", " ").title()
    star_symbols = "⭐" * stars
    new_title = f"{star_symbols} {role_title}"

    return {
        "stars": star_symbols,
        "new_title": new_title,
        "role": role,
        "score": score,
    }


def labs_step() -> None:
    """Main Labs Fictive step orchestrator.

    Guides users through the mission workflow:
      1. Profile learner readiness
      2. Select role
      3. Generate/select mission
      4. (User completes project)
      5. Evaluate and award progression
    """
    display_mission_header()

    # Step 1: Profile learner
    profile = profile_learner()
    if not profile:
        return

    # Step 2: Select role
    role = select_role()
    if not role:
        return

    # Step 3: Generate or suggest mission
    mission = generate_or_suggest_mission(profile, role)
    if not mission:
        return

    # Save mission
    if not save_mission(mission, profile, role):
        return

    # Offer evaluation path
    console.print("\n[yellow]Next Steps:[/yellow]")
    console.print(f"1️⃣  Clone the project skeleton or start from scratch")
    console.print("2️⃣  Build the project in ~/labs or your project directory")
    console.print("3️⃣  Return to Labs step to evaluate your work")
    console.print()

    # Step 4: Evaluate mission (optional now, can do later)
    evaluate_now = Confirm.ask(
        "Do you want to evaluate your project now?",
        default=False,
    )
    if evaluate_now:
        evaluate_mission(profile, role, mission)

    console.print("\n[green]Mission workflow complete! Keep learning! 🚀[/green]\n")
