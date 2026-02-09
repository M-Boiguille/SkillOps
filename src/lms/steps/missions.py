"""Mission Control step - manage tickets and incidents."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import inquirer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from src.lms.classes.mission import Company, Mission
from src.lms.display import (
    display_error_message,
    display_info_panel,
    display_section_header,
    display_success_message,
)
from src.lms.steps.validator import validate_mission
from src.lms.steps.briefing import technical_briefing_step

console = Console()


def _load_companies() -> Dict[str, Company]:
    """Load fictitious companies from YAML."""
    companies_path = Path(__file__).parent.parent / "data" / "companies.yaml"
    try:
        with open(companies_path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        companies = {}
        for company_data in data.get("companies", []):
            company = Company.model_validate(company_data)
            companies[company.id] = company
        return companies
    except (FileNotFoundError, yaml.YAMLError, ValueError):
        return {}


def _load_missions() -> List[Mission]:
    """Load missions from data/missions/*.yaml files."""
    missions_dir = Path(__file__).parent.parent / "data" / "missions"
    missions: List[Mission] = []

    if not missions_dir.exists():
        return missions

    for mission_file in sorted(missions_dir.glob("*.yaml")):
        try:
            with open(mission_file, "r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except (FileNotFoundError, yaml.YAMLError):
            continue

        if isinstance(data, list):
            mission_items = data
        elif isinstance(data, dict) and "missions" in data:
            mission_items = data.get("missions", [])
        elif isinstance(data, dict):
            mission_items = [data]
        else:
            mission_items = []

        for mission_data in mission_items:
            try:
                missions.append(Mission.model_validate(mission_data))
            except ValueError:
                continue

    return sorted(missions, key=lambda mission: mission.id)


def _display_missions_table(
    missions: List[Mission], companies: Dict[str, Company]
) -> None:
    """Render a backlog table for mission selection."""
    table = Table(
        title="🛰️ Mission Backlog",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="cyan", width=4)
    table.add_column("Company", style="magenta", width=18)
    table.add_column("Title", style="white", width=45)
    table.add_column("Difficulty", style="yellow", width=14)
    table.add_column("ETA", style="green", width=10)

    for mission in missions:
        company_name = companies.get(
            mission.company_id,
            Company(
                id="unknown",
                name="Unknown",
                industry="",
                culture="",
            ),
        ).name
        table.add_row(
            str(mission.id),
            company_name,
            mission.title,
            mission.difficulty,
            mission.estimated_time,
        )

    console.print()
    console.print(table)


def _display_mission_details(mission: Mission, company: Company | None) -> None:
    """Show mission details and acceptance criteria."""
    company_name = company.name if company else "Unknown"

    console.print(
        Panel(
            f"[bold cyan]{mission.title}[/bold cyan]\n" f"[dim]{company_name}[/dim]",
            border_style="cyan",
        )
    )

    display_info_panel("Contexte", mission.scenario, border_color="blue")

    if mission.objectives:
        objectives = "\n".join(f"- {item}" for item in mission.objectives)
        display_info_panel("Objectifs", objectives, border_color="magenta")

    if mission.acceptance_criteria:
        criteria = "\n".join(f"- {item}" for item in mission.acceptance_criteria)
        display_info_panel("Critères d'acceptation", criteria, border_color="green")

    if mission.hints:
        hints = "\n".join(f"- {item}" for item in mission.hints)
        display_info_panel("Indices", hints, border_color="yellow")


def missions_step() -> None:
    """Mission Control main workflow."""
    display_section_header("Mission Control", "🛰️")

    companies = _load_companies()
    missions = _load_missions()

    if not missions:
        display_error_message(
            "Aucune mission disponible",
            "Vérifiez le dossier data/missions",
        )
        return

    _display_missions_table(missions, companies)

    choices = []
    for mission in missions:
        company = companies.get(
            mission.company_id,
            Company(id="unknown", name="Unknown", industry="", culture=""),
        )
        choices.append(f"{mission.id}. [{company.name}] {mission.title}")
    choices.append("⬅️  Retour au menu principal")

    questions = [
        inquirer.List(
            "mission",
            message="Choisissez une mission",
            choices=choices,
            carousel=True,
        )
    ]

    try:
        answers = inquirer.prompt(questions)
        if answers is None:
            console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
            return
    except KeyboardInterrupt:
        console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
        return

    selection = answers.get("mission")
    if selection == "⬅️  Retour au menu principal":
        return

    selected_id = int(selection.split(".")[0])
    mission = next((item for item in missions if item.id == selected_id), None)

    if not mission:
        display_error_message("Mission introuvable", "Veuillez réessayer.")
        return

    company = companies.get(mission.company_id)
    _display_mission_details(mission, company)

    action_choices = [
        "🆘 Demander un briefing technique",
        "✅ Marquer la mission comme terminée",
        "⬅️  Retour au menu principal",
    ]

    action_questions = [
        inquirer.List(
            "action",
            message="Que souhaitez-vous faire ?",
            choices=action_choices,
            carousel=True,
        )
    ]

    try:
        action_answers = inquirer.prompt(action_questions)
        if action_answers is None:
            console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
            return
    except KeyboardInterrupt:
        console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
        return

    action = action_answers.get("action")
    if action == "⬅️  Retour au menu principal":
        return

    if action == "🆘 Demander un briefing technique":
        technical_briefing_step(context=mission.scenario)
        if not Confirm.ask("Marquer cette mission comme terminée ?", default=False):
            console.print("\n[dim]Mission laissée en cours.[/dim]\n")
            return
    else:
        if not Confirm.ask("Marquer cette mission comme terminée ?", default=False):
            console.print("\n[dim]Mission laissée en cours.[/dim]\n")
            return

    result = validate_mission(mission)

    if result.passed:
        display_success_message(
            "Mission validée. Bien joué !",
            title="Mission Control",
        )
    else:
        failures = "\n".join(f"- {item}" for item in result.failures)
        display_error_message(
            "Validation incomplète",
            failures or "Veuillez réessayer.",
        )
