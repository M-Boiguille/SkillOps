"""On-Call incident simulation module for SkillOps.

Generates realistic incidents to train debugging and troubleshooting skills.
"""

import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.lms.database import get_connection, init_db

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


# Incident templates
INCIDENT_TEMPLATES = [
    {
        "severity": "P1",
        "title": "Database connection pool exhausted",
        "description": (
            "The application cannot acquire database connections. "
            "Response time degraded to 5+ seconds."
        ),
        "affected_system": "PostgreSQL",
        "symptoms": (
            "HTTP 500 errors, timeout exceptions in logs, " "connection pool at 100%"
        ),
    },
    {
        "severity": "P2",
        "title": "High memory usage on API pods",
        "description": (
            "Memory usage consistently above 90% on 3/5 API pods. " "Risk of OOMKill."
        ),
        "affected_system": "Kubernetes API deployment",
        "symptoms": (
            "kubectl top shows >90% memory, " "pods restarting intermittently"
        ),
    },
    {
        "severity": "P2",
        "title": "Slow query degrading performance",
        "description": (
            "Database query execution time increased from 50ms to 800ms. "
            "Missing index suspected."
        ),
        "affected_system": "MySQL",
        "symptoms": (
            "Slow query log shows SELECT * queries, " "users report slow page loads"
        ),
    },
    {
        "severity": "P1",
        "title": "Service mesh routing failure",
        "description": (
            "50% of requests to payment-service returning 503. "
            "Istio sidecar misconfigured."
        ),
        "affected_system": "Istio service mesh",
        "symptoms": (
            "Intermittent 503 errors, traffic not balanced, "
            "envoy logs show upstream errors"
        ),
    },
    {
        "severity": "P3",
        "title": "Certificate expiring in 7 days",
        "description": (
            "TLS certificate for api.example.com expires on 2026-02-18. "
            "Renewal needed."
        ),
        "affected_system": "Ingress controller",
        "symptoms": (
            "cert-manager alert, kubectl describe shows " "NotAfter date approaching"
        ),
    },
    {
        "severity": "P2",
        "title": "Redis cache hit rate dropped to 30%",
        "description": (
            "Normal hit rate is 85%. Cache evictions increased 10x. "
            "Memory pressure suspected."
        ),
        "affected_system": "Redis",
        "symptoms": (
            "redis-cli INFO shows low hit rate, " "evicted_keys metric spiking"
        ),
    },
    {
        "severity": "P1",
        "title": "DNS resolution failing for external services",
        "description": (
            "Cannot resolve external APIs. " "CoreDNS pods in CrashLoopBackOff."
        ),
        "affected_system": "CoreDNS",
        "symptoms": (
            "nslookup fails, pods cannot reach external endpoints, "
            "DNS timeout errors"
        ),
    },
    {
        "severity": "P2",
        "title": "Disk usage at 95% on worker nodes",
        "description": (
            "Worker nodes running out of disk space. " "Log rotation not working."
        ),
        "affected_system": "Kubernetes nodes",
        "symptoms": (
            "df -h shows 95% usage, pod evictions starting, " "disk pressure taints"
        ),
    },
]


def create_incident(
    storage_path: Optional[Path] = None, template: Optional[dict] = None
) -> Incident:
    """Create a new incident (random or from template).

    Args:
        storage_path: Custom storage directory
        template: Optional incident template dict

    Returns:
        Created Incident object
    """
    init_db(storage_path)

    if template is None:
        template = random.choice(INCIDENT_TEMPLATES)

    incident = Incident(
        id=None,
        timestamp=datetime.now().isoformat(),
        severity=template["severity"],
        title=template["title"],
        description=template["description"],
        affected_system=template["affected_system"],
        symptoms=template["symptoms"],
        status="open",
    )

    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO incidents (timestamp, severity, title, description,
                               affected_system, symptoms, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            incident.timestamp,
            incident.severity,
            incident.title,
            incident.description,
            incident.affected_system,
            incident.symptoms,
            incident.status,
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
               affected_system, symptoms, status, resolution, postmortem_id
        FROM incidents
        WHERE status != 'resolved'
        ORDER BY timestamp DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    incidents = []
    for row in rows:
        incidents.append(
            Incident(
                id=row[0],
                timestamp=row[1],
                severity=row[2],
                title=row[3],
                description=row[4],
                affected_system=row[5],
                symptoms=row[6],
                status=row[7],
                resolution=row[8],
                postmortem_id=row[9],
            )
        )
    return incidents


def update_incident_status(
    incident_id: int,
    status: str,
    resolution: Optional[str] = None,
    storage_path: Optional[Path] = None,
) -> None:
    """Update incident status.

    Args:
        incident_id: Incident ID
        status: New status (investigating, resolved)
        resolution: Resolution description (for resolved status)
        storage_path: Custom storage directory
    """
    init_db(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE incidents
        SET status = ?, resolution = ?
        WHERE id = ?
        """,
        (status, resolution, incident_id),
    )
    conn.commit()
    conn.close()


def display_incident(incident: Incident) -> None:
    """Display incident details with Rich formatting."""
    severity_colors = {
        "P1": "red",
        "P2": "yellow",
        "P3": "cyan",
        "P4": "green",
    }
    color = severity_colors.get(incident.severity, "white")

    content = f"""[bold {color}]{incident.severity} - {incident.title}[/bold {color}]

📅 Time: {incident.timestamp}
🎯 System: {incident.affected_system}
📊 Status: {incident.status.upper()}

[bold]Description:[/bold]
{incident.description}

[bold]Symptoms:[/bold]
{incident.symptoms}

[bold]Your mission:[/bold]
1. Investigate the root cause
2. Implement a fix
3. Verify the system is healthy
4. Document your findings in a post-mortem
"""

    panel = Panel(
        content,
        title=f"🚨 Incident #{incident.id}",
        border_style=color,
        padding=(1, 2),
    )
    console.print(panel)


def oncall_step(storage_path: Optional[Path] = None) -> bool:
    """Run the on-call step (interactive incident handling).

    Args:
        storage_path: Custom storage directory

    Returns:
        True if step completed successfully
    """
    console.print("\n[bold cyan]🚨 On-Call Incident Dashboard[/bold cyan]\n")

    # Check for open incidents
    open_incidents = get_open_incidents(storage_path)

    if open_incidents:
        console.print(
            f"[yellow]⚠️  You have {len(open_incidents)} open incident(s)[/yellow]\n"
        )
        for inc in open_incidents:
            severity_emoji = "🔴" if inc.severity == "P1" else "🟡"
            console.print(
                f"{severity_emoji} [{inc.severity}] {inc.title} (ID: {inc.id})"
            )

        console.print()
        action = Prompt.ask(
            "What would you like to do?",
            choices=["view", "resolve", "new", "quit"],
            default="view",
        )

        if action == "view":
            incident_id = Prompt.ask("Enter incident ID to view")
            try:
                incident_id = int(incident_id)
                incident = next(
                    (i for i in open_incidents if i.id == incident_id), None
                )
                if incident:
                    display_incident(incident)
                    return True
                else:
                    console.print("[red]Incident not found[/red]")
                    return False
            except ValueError:
                console.print("[red]Invalid incident ID[/red]")
                return False

        elif action == "resolve":
            incident_id = Prompt.ask("Enter incident ID to resolve")
            try:
                incident_id = int(incident_id)
                resolution = Prompt.ask("Enter resolution summary")
                update_incident_status(
                    incident_id, "resolved", resolution, storage_path
                )
                console.print(
                    f"[green]✅ Incident #{incident_id} marked as resolved[/green]"
                )
                console.print(
                    "[yellow]💡 Don't forget to write a post-mortem: skillops post-mortem[/yellow]"
                )
                return True
            except ValueError:
                console.print("[red]Invalid incident ID[/red]")
                return False

        elif action == "quit":
            return True

    # Generate new incident
    console.print("[bold]Generating new incident...[/bold]\n")
    incident = create_incident(storage_path)
    display_incident(incident)

    console.print(
        "\n[yellow]💡 Tip: Use 'skillops oncall' again to update incident status[/yellow]"
    )
    console.print(
        "[yellow]💡 After resolution, document with 'skillops post-mortem'[/yellow]\n"
    )

    return True
