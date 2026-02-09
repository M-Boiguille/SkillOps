"""PagerDuty Check - incident interceptor (Chaos Monkey)."""

from __future__ import annotations

import os
import random
from typing import Callable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from src.lms.display import display_section_header

console = Console()


def _get_incident_chance() -> float:
    try:
        return float(os.getenv("SKILLOPS_INCIDENT_CHANCE", "0.15"))
    except ValueError:
        return 0.15


def pagerduty_check(on_incident: Optional[Callable[[], None]] = None) -> bool:
    """Run the PagerDuty check before starting the main workflow.

    Returns:
        True to continue to menu, False to exit early.
    """
    display_section_header("PagerDuty Check", "🚨")

    force_incident = os.getenv("SKILLOPS_FORCE_INCIDENT", "").lower() in {
        "1",
        "true",
        "yes",
    }
    chance = _get_incident_chance()
    incident_triggered = force_incident or (random.random() < chance)

    if not incident_triggered:
        console.print(Panel("Aucun incident critique détecté.", border_style="green"))
        return True

    console.print(
        Panel(
            "Incident critique détecté !\nUn service est dégradé.",
            title="🚨 PagerDuty",
            border_style="red",
        )
    )

    handle_now = Confirm.ask("Intervenir immédiatement ?", default=True)
    if handle_now and on_incident:
        on_incident()
        return True

    return Confirm.ask("Continuer vers le menu principal ?", default=True)
