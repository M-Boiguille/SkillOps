"""On-Call incident simulation module for SkillOps.

AI-powered incident generation with spaced repetition and progressive hints.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

from src.lms.database import get_connection, init_db
from src.lms.oncall_ai import (
    calculate_next_review_date,
    generate_hints_for_incident,
    generate_incident_with_ai,
    generate_validation_questions,
    get_due_incidents,
)

console = Console()


@dataclass
class Incident:
    """Represents an on-call incident."""

    id: Optional[int]
    timestamp: str
    severity: str  # P1 (critical), P2 (high), P3 (medium), P4 (low)
    title: str
    description: str
    affected_system: str
    symptoms: str
    status: str  # open, investigating, resolved
    resolution: Optional[str] = None
    postmortem_id: Optional[int] = None
    resolution_score: Optional[int] = None
    next_review_date: Optional[str] = None
    hints_used: int = 0
    difficulty_level: int = 1
    generated_by: str = "ai"


def create_incident(
    storage_path: Optional[Path] = None, use_ai: bool = True
) -> Incident:
    """Create a new incident using AI generation.

    Args:
        storage_path: Custom storage directory
        use_ai: Use AI generation (default: True)

    Returns:
        Created Incident object
    """
    init_db(storage_path)

    if use_ai:
        try:
            incident_data = generate_incident_with_ai(storage_path=storage_path)
        except (ValueError, Exception) as e:
            console.print(f"[red]AI generation failed: {e}[/red]")
            console.print("[yellow]Set GEMINI_API_KEY to enable AI incidents[/yellow]")
            return None
    else:
        # Fallback to simple incident (should not happen in AI-only mode)
        incident_data = {
            "severity": "P2",
            "title": "Generic system issue",
            "description": "System experiencing issues",
            "affected_system": "Unknown",
            "symptoms": "To be investigated",
            "difficulty_level": 1,
            "generated_by": "fallback",
        }

    incident = Incident(
        id=None,
        timestamp=datetime.now().isoformat(),
        severity=incident_data["severity"],
        title=incident_data["title"],
        description=incident_data["description"],
        affected_system=incident_data["affected_system"],
        symptoms=incident_data["symptoms"],
        status="open",
        difficulty_level=incident_data.get("difficulty_level", 1),
        generated_by=incident_data.get("generated_by", "ai"),
    )

    conn = get_connection(storage_path)
    cursor = conn.cursor()

    # Convert lists to JSON for SQLite storage
    symptoms_json = (
        json.dumps(incident.symptoms)
        if isinstance(incident.symptoms, list)
        else incident.symptoms
    )

    cursor.execute(
        """
        INSERT INTO incidents (timestamp, severity, title, description,
                               affected_system, symptoms, status,
                               difficulty_level, generated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident.timestamp,
            incident.severity,
            incident.title,
            incident.description,
            incident.affected_system,
            symptoms_json,
            incident.status,
            incident.difficulty_level,
            incident.generated_by,
        ),
    )
    incident.id = cursor.lastrowid
    conn.commit()
    conn.close()

    return incident


def get_open_incidents(storage_path: Optional[Path] = None) -> list[Incident]:
    """Get all open incidents.

    Args:
        storage_path: Custom storage directory

    Returns:
        List of open Incident objects
    """
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, timestamp, severity, title, description,
               affected_system, symptoms, status, resolution, postmortem_id,
               resolution_score, next_review_date, hints_used, difficulty_level,
               generated_by
        FROM incidents
        WHERE status != 'resolved'
        ORDER BY timestamp DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    incidents = []
    for row in rows:
        # Decode JSON symptoms if it's a string
        symptoms = row[6]
        if isinstance(symptoms, str):
            try:
                symptoms = json.loads(symptoms)
            except json.JSONDecodeError:
                # Fallback: keep as string if not valid JSON
                pass

        incidents.append(
            Incident(
                id=row[0],
                timestamp=row[1],
                severity=row[2],
                title=row[3],
                description=row[4],
                affected_system=row[5],
                symptoms=symptoms,
                status=row[7],
                resolution=row[8],
                postmortem_id=row[9],
                resolution_score=row[10],
                next_review_date=row[11],
                hints_used=row[12],
                difficulty_level=row[13],
                generated_by=row[14],
            )
        )
    return incidents


def update_incident_status(
    incident_id: int,
    status: str,
    resolution: Optional[str] = None,
    storage_path: Optional[Path] = None,
    resolution_score: Optional[int] = None,
    hints_used: Optional[int] = None,
) -> None:
    """Update incident status with SRS fields.

    Args:
        incident_id: Incident ID
        status: New status (investigating, resolved)
        resolution: Resolution description (for resolved status)
        storage_path: Custom storage directory
        resolution_score: Score from 0-5 for SRS scheduling
        hints_used: Number of hints used
    """
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()

    # Calculate next review date if scoring
    next_review = None
    if resolution_score is not None:
        next_review = calculate_next_review_date(resolution_score)

    cursor.execute(
        """
        UPDATE incidents
        SET status = ?, resolution = ?, resolution_score = ?,
            next_review_date = ?, hints_used = ?
        WHERE id = ?
        """,
        (status, resolution, resolution_score, next_review, hints_used, incident_id),
    )
    conn.commit()
    conn.close()


def display_incident(incident: Incident, show_hints_button: bool = True) -> None:
    """Display incident details with Rich formatting.

    Args:
        incident: Incident object to display
        show_hints_button: Show hint availability message
    """
    severity_colors = {
        "P1": "red",
        "P2": "yellow",
        "P3": "cyan",
        "P4": "green",
    }
    color = severity_colors.get(incident.severity, "white")

    difficulty_stars = "⭐" * incident.difficulty_level

    content = f"""[bold {color}]{incident.severity} - {incident.title}[/bold {color}]

📅 Time: {incident.timestamp}
🎯 System: {incident.affected_system}
📊 Status: {incident.status.upper()}
{difficulty_stars} Difficulty: {incident.difficulty_level}/5

[bold]Description:[/bold]
{incident.description}

[bold]Symptoms:[/bold]
{incident.symptoms}

[bold]Your mission:[/bold]
1. Investigate the root cause
2. Implement a fix
3. Verify the system is healthy
4. Answer validation questions
"""

    if show_hints_button and incident.status == "open":
        hints_emoji = (
            "💡" if incident.hints_used == 0 else f"💡 ({incident.hints_used} used)"
        )
        content += f"\n{hints_emoji} Type 'hint' to get progressive help (costs points)"

    panel = Panel(
        content,
        title=f"🚨 Incident #{incident.id}",
        border_style=color,
        padding=(1, 2),
    )
    console.print(panel)


def request_hint_for_incident(
    incident: Incident, storage_path: Optional[Path] = None
) -> str:
    """Request a progressive hint for an incident.

    Args:
        incident: Active incident
        storage_path: Custom storage directory

    Returns:
        Hint text
    """
    if incident.hints_used >= 3:
        return "❌ No more hints available (max 3 per incident)"

    next_hint_level = incident.hints_used + 1
    point_cost = 0 if next_hint_level == 1 else 1 if next_hint_level == 2 else 2

    console.print(f"\n[yellow]💡 Requesting hint level {next_hint_level}/3...[/yellow]")
    if point_cost > 0:
        console.print(
            f"[dim](This will cost -{point_cost} points from final score)[/dim]"
        )

    try:
        hint_text = generate_hints_for_incident(
            incident.id, next_hint_level, storage_path=storage_path
        )

        # Update hints_used counter
        init_db(storage_path)
        conn = get_connection(storage_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE incidents SET hints_used = ? WHERE id = ?",
            (next_hint_level, incident.id),
        )
        conn.commit()
        conn.close()

        incident.hints_used = next_hint_level

        hint_labels = {1: "Socratic Question", 2: "Direction", 3: "Specific Command"}
        label = hint_labels.get(next_hint_level, "Hint")

        console.print(f"\n[bold cyan]{label}:[/bold cyan]")
        console.print(f"[italic]{hint_text}[/italic]\n")

        return hint_text

    except Exception as e:
        console.print(f"[red]Failed to generate hint: {e}[/red]")
        return ""


def validate_resolution(
    incident: Incident, resolution: str, storage_path: Optional[Path] = None
) -> int:
    """Validate incident resolution with AI questions.

    Args:
        incident: Resolved incident
        resolution: User's resolution description
        storage_path: Custom storage directory

    Returns:
        Final score (0-5)
    """
    console.print("\n[bold cyan]📝 Validation Questions[/bold cyan]\n")
    console.print("[dim]Answer these to demonstrate your understanding...[/dim]\n")

    try:
        questions = generate_validation_questions(
            incident.id, resolution, storage_path=storage_path
        )

        if not questions:
            console.print("[yellow]⚠️  Could not generate validation questions[/yellow]")
            console.print("[dim]Skipping validation...[/dim]\n")
            base_score = 3
        else:
            answers = []
            for i, question in enumerate(questions, 1):
                console.print(f"[bold]Q{i}:[/bold] {question}")
                answer = Prompt.ask("Your answer")
                answers.append(answer)
                console.print()

            # Simple scoring: full points if attempted all questions
            base_score = 4 if len(answers) == len(questions) else 3

    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        base_score = 3

    # Deduct points for hints used
    final_score = max(0, base_score - incident.hints_used)

    console.print(f"[bold cyan]Base score: {base_score}/5[/bold cyan]")
    if incident.hints_used > 0:
        console.print(f"[yellow]Hints penalty: -{incident.hints_used}[/yellow]")
    console.print(f"[bold green]Final score: {final_score}/5[/bold green]\n")

    return final_score


def oncall_step(storage_path: Optional[Path] = None) -> bool:
    """Run the on-call step with AI incidents and SRS.

    Args:
        storage_path: Custom storage directory

    Returns:
        True if step completed successfully
    """
    console.print(
        "\n[bold cyan]🚨 On-Call Incident Dashboard (AI-Powered)[/bold cyan]\n"
    )

    # Check for incidents due for review (SRS)
    due_incidents = get_due_incidents(storage_path)
    if due_incidents:
        msg = (
            f"[magenta]📅 {len(due_incidents)} incident(s) due for review "
            f"(spaced repetition)[/magenta]"
        )
        console.print(msg)
        console.print(
            "[dim]These are similar to incidents you struggled with before[/dim]\n"
        )

    # Check for open incidents
    open_incidents = get_open_incidents(storage_path)

    if open_incidents:
        console.print(
            f"[yellow]⚠️  You have {len(open_incidents)} active incident(s)[/yellow]\n"
        )
        for inc in open_incidents:
            severity_emoji = "🔴" if inc.severity == "P1" else "🟡"
            hints_indicator = f" (💡×{inc.hints_used})" if inc.hints_used > 0 else ""
            msg = (
                f"{severity_emoji} [{inc.severity}] {inc.title} "
                f"(ID: {inc.id}){hints_indicator}"
            )
            console.print(msg)

        console.print()
        action = Prompt.ask(
            "What would you like to do?",
            choices=["investigate", "hint", "resolve", "new", "quit"],
            default="investigate",
        )

        if action == "investigate":
            incident_id = IntPrompt.ask("Enter incident ID to investigate")
            incident = next((i for i in open_incidents if i.id == incident_id), None)
            if incident:
                display_incident(incident)
                return True
            else:
                console.print("[red]❌ Incident not found[/red]")
                return False

        elif action == "hint":
            incident_id = IntPrompt.ask("Enter incident ID for hint")
            incident = next((i for i in open_incidents if i.id == incident_id), None)
            if incident:
                request_hint_for_incident(incident, storage_path)
                return True
            else:
                console.print("[red]❌ Incident not found[/red]")
                return False

        elif action == "resolve":
            incident_id = IntPrompt.ask("Enter incident ID to resolve")
            incident = next((i for i in open_incidents if i.id == incident_id), None)

            if not incident:
                console.print("[red]❌ Incident not found[/red]")
                return False

            console.print("\n[bold]Describe your resolution:[/bold]")
            resolution = Prompt.ask("What did you do to fix the issue?")

            # Validate with AI questions and score
            score = validate_resolution(incident, resolution, storage_path)

            # Update incident with score and schedule next review
            update_incident_status(
                incident_id,
                "resolved",
                resolution,
                storage_path,
                resolution_score=score,
                hints_used=incident.hints_used,
            )

            # Show SRS feedback
            if score >= 4:
                console.print("[green]✅ Excellent! Next review in 1 week[/green]")
            elif score >= 3:
                console.print("[cyan]✅ Good! Next review in 3 days[/cyan]")
            else:
                console.print(
                    "[yellow]⚠️  Needs practice. Next review in 1 day[/yellow]"
                )

            console.print(
                "\n[yellow]💡 Write a post-mortem: skillops post-mortem[/yellow]\n"
            )
            return True

        elif action == "quit":
            return True

    # Generate new AI incident
    console.print("[bold]🤖 Generating AI incident based on your history...[/bold]\n")

    incident = create_incident(storage_path, use_ai=True)

    if not incident:
        console.print("[red]❌ Failed to generate incident[/red]")
        console.print(
            "[yellow]Set GEMINI_API_KEY environment variable to enable AI generation[/yellow]"
        )
        return False

    display_incident(incident)

    console.print(
        "\n[yellow]💡 What would you like to do with this incident?[/yellow]\n"
    )

    # Interactive loop for the newly generated incident
    action = Prompt.ask(
        "Choose action",
        choices=["investigate", "hint", "resolve", "quit"],
        default="investigate",
    )

    if action == "investigate":
        display_incident(incident)
        console.print(
            "\n[dim]Run 'skillops oncall' again to continue working on this incident[/dim]"
        )
        return True

    elif action == "hint":
        request_hint_for_incident(incident, storage_path)
        console.print(
            "\n[dim]Run 'skillops oncall' again to continue working on this incident[/dim]"
        )
        return True

    elif action == "resolve":
        console.print("\n[bold]Describe your resolution:[/bold]")
        resolution = Prompt.ask("Resolution")

        # Validate with AI
        validation_passed = validate_resolution(incident, resolution, storage_path)

        # Update incident
        update_incident_status(incident.id, "resolved", resolution, storage_path)
        console.print("\n[green]✅ Incident resolved![/green]")

        if validation_passed:
            console.print("[cyan]✅ Good! Next review in 3 days[/cyan]")
        else:
            console.print("[yellow]⚠️  Needs practice. Next review in 1 day[/yellow]")

        console.print(
            "\n[yellow]💡 Write a post-mortem: skillops post-mortem[/yellow]\n"
        )
        return True

    elif action == "quit":
        return True

    return True
