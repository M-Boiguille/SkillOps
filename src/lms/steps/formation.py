"""Formation step - Active Recall & Tracking."""

import datetime  # noqa: F401
import os
import time
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.lms.api_clients.wakatime_client import WakaTimeClient, WakaTimeError
from src.lms.persistence import save_formation_log

console = Console()


def _save_session_log(
    goals: List[str], recall: str, duration_min: int, wakatime_minutes: int = 0
) -> None:
    """Sauvegarde le journal de session pour la revue future."""
    save_formation_log(goals, recall, duration_min, wakatime_minutes=wakatime_minutes)


def formation_step() -> bool:
    """
    Exécute l'étape de formation avec la méthode Active Recall.
    1. Priming (Objectifs)
    2. Session (Tracking)
    3. Exit Ticket (Active Recall)
    """
    console.clear()
    console.print(Panel.fit("⏱️  Formation - Deep Work Session", style="bold blue"))

    # --- PHASE 1: PRIMING (Amorçage) ---
    console.print("\n[bold yellow]🧠 Phase 1: Priming[/bold yellow]")
    console.print("Définissez 1 à 3 objectifs précis pour cette session.")
    console.print(
        "[italic]Ex: 'Comprendre la différence entre CMD et ENTRYPOINT'[/italic]"
    )

    goals: list[str] = []
    for i in range(3):
        goal = Prompt.ask(f"Objectif {i + 1} (Laisser vide pour terminer)", default="")
        if not goal and goals:
            break
        if goal:
            goals.append(goal)

    if not goals:
        console.print(
            "[red]Il faut au moins un objectif pour apprendre efficacement ![/red]"
        )
        return False

    # --- PHASE 2: SESSION (Tracking) ---
    console.print("\n[bold green]🚀 Phase 2: Session en cours...[/bold green]")
    console.print(f"Focus sur : {', '.join(goals)}")
    console.print(
        "Le tracking WakaTime est actif. Appuyez sur [bold]Entrée[/bold] quand vous avez fini."
    )

    start_time = time.time()

    # Simulation d'attente de fin de session
    Prompt.ask("")

    end_time = time.time()
    duration_min = int((end_time - start_time) / 60)

    # Appel API WakaTime pour vérifier le temps réel codé
    wakatime_minutes = 0
    try:
        waka_stats = WakaTimeClient(os.getenv("WAKATIME_API_KEY", "")).get_today_stats()
        console.print(f"Temps WakaTime aujourd'hui : {waka_stats.get('text', 'N/A')}")
        wakatime_minutes = int(waka_stats.get("total_seconds", 0) // 60)
    except WakaTimeError:
        console.print(
            "[yellow]Impossible de récupérer les stats WakaTime (API Key manquante ?)[/yellow]"
        )

    console.print(f"Session terminée. Durée estimée : {duration_min} min.")

    # --- PHASE 3: EXIT TICKET (Active Recall) ---
    console.print(
        "\n[bold magenta]🛑 Phase 3: Active Recall (Exit Ticket)[/bold magenta]"
    )
    console.print(
        "Sans regarder vos notes, résumez ce que vous avez appris en une phrase "
        "ou des bullet points."
    )
    console.print(
        "[italic]C'est l'étape la plus importante pour la mémorisation à long terme.[/italic]"
    )

    recall = ""
    while len(recall) < 10:
        recall = Prompt.ask("📝 Résumé")
        if len(recall) < 10:
            console.print(
                "[red]C'est un peu court. Faites un effort de synthèse ![/red]"
            )

    # Sauvegarde
    _save_session_log(goals, recall, duration_min, wakatime_minutes=wakatime_minutes)

    console.print(
        Panel(
            "✅ Session enregistrée ! Ces notes serviront pour la Review de demain.",
            style="green",
        )
    )
    return True
