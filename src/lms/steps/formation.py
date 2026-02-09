"""Étape Formation - Affichage des statistiques de temps de code WakaTime."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from ..api_clients.wakatime_client import WakaTimeClient, WakaTimeError
from ..display import (
    display_error_message,
    display_info_panel,
    display_section_header,
    display_success_message,
    display_warning_message,
    format_time_duration,
)

console = Console()

# Configuration
MINIMUM_DAILY_HOURS = 2
ALERT_TIME_HOUR = 17  # 17h


def get_api_key_from_env() -> Optional[str]:
    """
    Récupère la clé API WakaTime depuis les variables d'environnement.

    Returns:
        Optional[str]: La clé API ou None si non trouvée
    """
    return os.getenv("WAKATIME_API_KEY")


def should_show_alert(current_time: datetime, hours_coded: float) -> bool:
    """
    Détermine si une alerte doit être affichée.

    Une alerte est affichée si:
    - Il est avant l'heure limite (17h)
    - Le temps de code est inférieur au minimum requis

    Args:
        current_time: Heure actuelle
        hours_coded: Nombre d'heures de code aujourd'hui

    Returns:
        bool: True si l'alerte doit être affichée
    """
    is_before_deadline = current_time.hour < ALERT_TIME_HOUR
    below_minimum = hours_coded < MINIMUM_DAILY_HOURS
    return is_before_deadline and below_minimum


def create_stats_table(stats: dict) -> Table:
    """
    Crée un tableau Rich pour afficher les statistiques WakaTime.

    Args:
        stats: Dictionnaire avec les statistiques (total_seconds, languages, categories)

    Returns:
        Table: Tableau Rich avec les statistiques formatées
    """
    table = Table(
        title="📊 Statistiques du jour", show_header=True, header_style="bold cyan"
    )
    table.add_column("Métrique", style="cyan", width=20)
    table.add_column("Valeur", style="green", width=30)

    # Temps total
    total_seconds = stats.get("total_seconds", 0)
    formatted_time = format_time_duration(total_seconds)
    table.add_row("⏱️ Temps total", formatted_time)

    # Langages
    languages = stats.get("languages", [])
    if languages:
        top_language = languages[0]
        lang_name = top_language.get("name", "N/A")
        lang_time = format_time_duration(top_language.get("total_seconds", 0))
        table.add_row("💻 Langage principal", f"{lang_name} ({lang_time})")

    # Catégories
    categories = stats.get("categories", [])
    if categories:
        top_category = categories[0]
        cat_name = top_category.get("name", "N/A")
        cat_time = format_time_duration(top_category.get("total_seconds", 0))
        table.add_row("📁 Catégorie principale", f"{cat_name} ({cat_time})")

    return table


def create_languages_table(languages: list) -> Table:
    """
    Crée un tableau détaillé des langages utilisés.

    Args:
        languages: Liste des langages avec leurs statistiques

    Returns:
        Table: Tableau Rich avec les langages
    """
    table = Table(
        title="💻 Langages utilisés", show_header=True, header_style="bold magenta"
    )
    table.add_column("Langage", style="magenta", width=20)
    table.add_column("Temps", style="cyan", width=15)
    table.add_column("Pourcentage", style="green", width=15)

    for lang in languages[:5]:  # Top 5
        name = lang.get("name", "N/A")
        time_str = format_time_duration(lang.get("total_seconds", 0))
        percent = lang.get("percent", 0)
        table.add_row(name, time_str, f"{percent:.1f}%")

    return table


def formation_step(storage_path: Optional[Path] = None) -> None:
    """
    Exécute l'étape Formation : affiche les statistiques WakaTime du jour.

    Cette fonction:
    1. Récupère la clé API WakaTime
    2. Interroge l'API pour les stats du jour
    3. Affiche un résumé des statistiques
    4. Affiche une alerte si le temps de code est insuffisant (< 2h avant 17h)
    5. Affiche les langages utilisés

    Args:
        storage_path: Chemin vers le répertoire de stockage (non utilisé pour l'instant)

    Raises:
        WakaTimeError: En cas d'erreur avec l'API WakaTime
    """
    display_section_header("Metrics", "📚")

    # Récupérer la clé API
    api_key = get_api_key_from_env()
    if not api_key:
        display_error_message(
            "Clé API WakaTime introuvable",
            "Veuillez définir la variable d'environnement WAKATIME_API_KEY.\n"
            "Consultez le README pour les instructions de configuration.",
        )
        return

    try:
        # Initialiser le client WakaTime
        client = WakaTimeClient(api_key)

        # Récupérer les stats du jour
        display_info_panel("WakaTime", "Récupération des statistiques...")
        stats = client.get_today_stats()

        # Afficher le tableau de statistiques
        console.print()
        stats_table = create_stats_table(stats)
        console.print(stats_table)

        # Calculer les heures de code
        total_seconds = stats.get("total_seconds", 0)
        hours_coded = total_seconds / 3600

        # Vérifier si une alerte doit être affichée
        current_time = datetime.now()
        if should_show_alert(current_time, hours_coded):
            remaining_hours = MINIMUM_DAILY_HOURS - hours_coded
            display_warning_message(
                "⚠️ Objectif quotidien non atteint",
                f"Il vous reste {remaining_hours:.1f}h à coder avant 17h pour atteindre "
                f"l'objectif de {MINIMUM_DAILY_HOURS}h.",
            )
        else:
            if hours_coded >= MINIMUM_DAILY_HOURS:
                display_success_message(
                    "🎉 Objectif quotidien atteint !",
                    f"Vous avez codé {hours_coded:.1f}h aujourd'hui. Excellent travail !",
                )

        # Afficher les langages si disponibles
        languages = stats.get("languages", [])
        if languages:
            console.print()
            languages_table = create_languages_table(languages)
            console.print(languages_table)

        console.print()

    except WakaTimeError as e:
        display_error_message("Erreur WakaTime", str(e))
        console.print(
            "\n[yellow]Conseil:[/yellow] Vérifiez que votre clé API WakaTime "
            "est valide sur https://wakatime.com/settings/account"
        )
