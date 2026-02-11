"""Étape Reinforce - Pratique d'exercices avec suivi de progression."""

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import inquirer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..display import (
    display_error_message,
    display_info_panel,
    display_section_header,
    display_success_message,
    format_time_duration,
)
from ..integrations.exercise_generator import ExerciseGenerator
from ..paths import get_storage_path as resolve_storage_path
from ..persistence import (
    save_reinforce_progress,
    get_latest_reinforce_progress,
    get_reinforce_history,
)

console = Console()


def _load_exercises_catalog() -> List[Dict]:
    """
    Charge le catalogue des exercices depuis exercises_catalog.yaml.

    Returns:
        List[Dict]: Liste des exercices du catalogue ou liste vide si non disponible
    """
    catalog_path = Path(__file__).parent.parent / "data" / "exercises_catalog.yaml"

    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("exercises", [])
    except (FileNotFoundError, yaml.YAMLError):
        # Fallback : retourne une liste vide
        return []


def get_available_domains() -> List[str]:
    """
    Retourne la liste des domaines/technologies disponibles.

    Returns:
        List[str]: Liste des domaines (Linux, Docker, Terraform, Kubernetes, AWS, GitLab CI)
    """
    return [
        "Linux",
        "Docker",
        "Terraform",
        "Kubernetes",
        "AWS",
        "GitLab CI",
    ]


def get_available_exercises() -> List[Dict]:
    """
    Retourne la liste des exercices disponibles du catalogue.

    Returns:
        List[Dict]: Liste des exercices avec id, key, titre, domaine, etc.
    """
    catalog = _load_exercises_catalog()
    return catalog


def get_storage_path() -> Path:
    """Récupère le chemin de stockage depuis l'environnement ou utilise le défaut."""
    return resolve_storage_path()


def display_exercises_table(exercises: List[Dict[str, str]]) -> None:
    """
    Affiche un tableau des exercices disponibles.

    Args:
        exercises: Liste des exercices à afficher
    """
    table = Table(
        title="📝 Exercices disponibles", show_header=True, header_style="bold cyan"
    )
    table.add_column("#", style="cyan", width=3)
    table.add_column("Domaine", style="magenta", width=18)
    table.add_column("Titre", style="white", width=45)
    table.add_column("Difficulté", style="yellow", width=15)
    table.add_column("Durée", style="green", width=10)

    for exercise in exercises:
        table.add_row(
            str(exercise.get("id", "?")),
            exercise.get("primary_domain", "N/A"),
            exercise.get("title", "N/A"),
            exercise.get("difficulty", "N/A"),
            exercise.get("estimated_time", "N/A"),
        )

    console.print()
    console.print(table)
    console.print()


def get_exercise_completion_count(exercise_id: str, storage_path: Path) -> int:
    """
    Compte le nombre de fois qu'un exercice a été complété avec succès.

    Args:
        exercise_id: Identifiant de l'exercice
        storage_path: Chemin vers le répertoire de stockage

    Returns:
        int: Nombre de complétions réussies (historique complet)
    """
    history = get_reinforce_history(exercise_id)
    return sum(1 for entry in history if entry.get("completed"))


def get_exercise_progress(exercise_id: str, storage_path: Path) -> Optional[Dict]:
    """
    Récupère la progression d'un exercice depuis le stockage.

    Args:
        exercise_id: Identifiant de l'exercice
        storage_path: Chemin vers le répertoire de stockage

    Returns:
        Optional[Dict]: Données de progression ou None si non trouvé
    """
    return get_latest_reinforce_progress(exercise_id)


def calculate_next_review(quality: int, previous_data: Dict) -> Dict:
    """
    Calcule la prochaine date de révision via l'algorithme SuperMemo-2 (SM-2).

    Args:
        quality: Note de 0 à 5 (0-2: échec, 3-5: succès)
        previous_data: Données de la dernière révision (interval, reps, ef)
    """
    reps = previous_data.get("reps", 0)
    interval = previous_data.get("interval", 0)
    ease_factor = previous_data.get("ease_factor", 2.5)

    if quality >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)
        reps += 1
    else:
        reps = 0
        interval = 1

    # Mise à jour de l'Ease Factor
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ease_factor = max(1.3, ease_factor)

    next_date = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")

    return {
        "reps": reps,
        "interval": interval,
        "ease_factor": ease_factor,
        "next_review": next_date,
    }


def save_exercise_progress(
    exercise_id: str,
    title: str,
    duration_seconds: int,
    completed: bool,
    storage_path: Path,
    quality: int = 4,  # Par défaut "Bon" si complété
) -> None:
    """
    Sauvegarde la progression d'un exercice.

    Args:
        exercise_id: Identifiant de l'exercice
        title: Titre de l'exercice
        duration_seconds: Durée en secondes
        completed: Si l'exercice est terminé
        storage_path: Chemin vers le répertoire de stockage
    """
    # Get previous SRS data
    latest = get_latest_reinforce_progress(exercise_id)
    # Récupérer les données SRS précédentes
    prev_srs = latest.get("srs_data", {}) if latest else {}

    srs_data = calculate_next_review(quality if completed else 1, prev_srs)

    save_reinforce_progress(
        exercise_id, title, duration_seconds, completed, quality, srs_data
    )


def display_exercise_content(exercise_content: Dict[str, str]) -> None:
    """Display the full exercise instructions.

    Args:
        exercise_content: Generated exercise content from AI
    """
    console.print("\n")
    console.print(
        Panel(
            f"[bold cyan]{exercise_content.get('title', 'Exercise')}[/bold cyan]",
            border_style="cyan",
        )
    )

    # Objectives
    console.print("\n[bold yellow]🎯 Objectifs d'apprentissage:[/bold yellow]")
    console.print(exercise_content.get("objectives", "N/A"))

    # Prerequisites
    if "prerequisites" in exercise_content:
        console.print("\n[bold yellow]📋 Prérequis:[/bold yellow]")
        console.print(exercise_content["prerequisites"])

    # Scenario
    if "scenario" in exercise_content:
        console.print("\n[bold yellow]🎬 Contexte / Mission:[/bold yellow]")
        console.print(exercise_content["scenario"])

    # Requirements (what to achieve, not how)
    console.print("\n[bold yellow]📋 Résultats attendus:[/bold yellow]")
    console.print(exercise_content.get("requirements", "N/A"))

    # Success criteria for self-evaluation
    console.print(
        "\n[bold yellow]✅ Critères de réussite (auto-évaluation):[/bold yellow]"
    )
    console.print(exercise_content.get("success_criteria", "N/A"))

    # Resources
    if "resources" in exercise_content:
        console.print("\n[bold yellow]📚 Documentation:[/bold yellow]")
        console.print(exercise_content["resources"])

    console.print("\n" + "─" * 80 + "\n")


def record_exercise_session(
    exercise: Dict[str, str],
    exercise_content: Dict[str, str],
    storage_path: Path,
) -> None:
    """
    Enregistre une session d'exercice avec chronomètre et validation.

    Args:
        exercise: Dictionnaire avec les métadonnées de l'exercice
        exercise_content: Contenu généré de l'exercice (instructions, etc.)
        storage_path: Chemin vers le répertoire de stockage
    """
    # Display full exercise instructions
    display_exercise_content(exercise_content)

    console.print(
        "[cyan]📌 Options:[/cyan]\n"
        "  [yellow]h[/yellow] - Voir les indices\n"
        "  [yellow]s[/yellow] - Voir la solution\n"
        "  [yellow]Enter[/yellow] - Commencer l'exercice\n"
    )

    choice = Prompt.ask("Votre choix", default="")

    if choice.lower() == "h":
        console.print("\n[bold yellow]💡 Indices:[/bold yellow]")
        console.print(exercise_content.get("hints", "Aucun indice disponible."))
        console.print("\n[cyan]Appuyez sur Entrée pour commencer...[/cyan]")
        input()
    elif choice.lower() == "s":
        console.print("\n[bold yellow]✨ Solution:[/bold yellow]")
        console.print(exercise_content.get("solution", "Solution non disponible."))
        console.print(
            "\n[yellow]⚠️  Essayez d'abord sans la solution pour mieux "
            "apprendre![/yellow]"
        )
        console.print("\n[cyan]Appuyez sur Entrée pour continuer...[/cyan]")
        input()

    console.print(
        "\n[cyan]⏱️  Chronomètre démarré ! Appuyez sur Entrée quand "
        "vous avez terminé...[/cyan]"
    )
    start_time = datetime.now()
    input()  # Attendre que l'utilisateur appuie sur Entrée

    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    # Auto-évaluation basée sur les critères de succès
    console.print("\n[bold cyan]📊 Auto-évaluation[/bold cyan]")
    console.print("\nRevisez les critères de réussite ci-dessus.")
    console.print("Avez-vous validé TOUS les critères ?\n")

    completed = Confirm.ask("✅ Succès ?", default=False)

    quality = 1
    if completed:
        # Demander la difficulté pour le SRS
        quality_str = Prompt.ask(
            "Difficulté (1=Impossible, 3=Dur, 4=Bon, 5=Facile)",
            choices=["1", "3", "4", "5"],
            default="4",
        )
        quality = int(quality_str)

    # Sauvegarder la progression
    save_exercise_progress(
        exercise["id"],
        exercise["title"],
        duration,
        completed,
        storage_path,
        quality=quality,
    )

    if completed:
        display_success_message(
            "Exercice terminé !",
            f"Durée : {format_time_duration(duration)}\n"
            f"Exercice : {exercise['title']}\n\n"
            f"Excellent travail ! 🎉",
        )
    else:
        display_info_panel(
            "Session enregistrée",
            f"Durée : {format_time_duration(duration)}\n"
            f"Exercice : {exercise['title']}\n\n"
            f"Continuez à pratiquer ! 💪",
        )


def get_daily_mix(exercises: List[Dict], storage_path: Path) -> List[Dict]:
    """Génère une liste d'exercices 'Daily Mix' (SRS + Interleaving)."""
    due_exercises = []
    other_exercises = []
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. Récupérer les exercices dus (SRS)
    for ex in exercises:
        prog = get_exercise_progress(ex.get("id"), storage_path)
        if prog and prog.get("srs_data", {}).get("next_review", "2999-01-01") <= today:
            due_exercises.append(ex)
        else:
            other_exercises.append(ex)

    # 2. Interleaving : Ajouter des exercices aléatoires non maîtrisés
    # On vise 3 exercices minimum : Priorité aux DUS, puis Random
    selection = due_exercises[:]

    # Identifier les domaines déjà présents pour maximiser l'Interleaving (Context Switching)
    used_domains = {ex.get("primary_domain") for ex in selection}

    if len(selection) < 3:
        needed = 3 - len(selection)

        # Prioriser les exercices dont le domaine n'est PAS encore dans la sélection
        priority_others = [
            ex for ex in other_exercises if ex.get("primary_domain") not in used_domains
        ]
        remaining_others = [
            ex for ex in other_exercises if ex.get("primary_domain") in used_domains
        ]

        random.shuffle(priority_others)
        random.shuffle(remaining_others)

        # Remplir avec la priorité d'abord, puis le reste si nécessaire
        candidates = priority_others + remaining_others
        selection.extend(candidates[:needed])

    # Limiter à 5 max pour ne pas surcharger
    return selection[:5]


def reinforce_step(storage_path: Optional[Path] = None) -> bool:
    """
    Exécute l'étape Reinforce : pratique d'exercices avec suivi de progression.

    Cette fonction:
    1. Affiche la liste des exercices disponibles
    2. Permet de choisir un exercice
    3. Génère ou charge l'exercice avec l'IA
    4. Enregistre la session avec chronomètre
    5. Sauvegarde la progression

    Args:
        storage_path: Chemin vers le répertoire de stockage (optionnel)
    """
    display_section_header("Reinforce - Pratique", "💪")

    # Déterminer le chemin de stockage
    if storage_path is None:
        storage_path = get_storage_path()

    # Récupérer les exercices disponibles
    exercises = get_available_exercises()

    if not exercises:
        display_error_message(
            "Aucun exercice disponible",
            "Le catalogue d'exercices est vide. Vérifiez exercises_catalog.yaml",
        )
        return False

    # Mode Daily Mix vs Catalogue
    console.print("\n[bold yellow]🧠 Mode d'entraînement[/bold yellow]")
    mode = inquirer.list_input(
        "Choisir le mode",
        choices=[
            "🎲 Daily Mix (Recommandé - SRS + Interleaving)",
            "📂 Catalogue complet",
        ],
    )

    if "Daily Mix" in mode:
        exercises = get_daily_mix(exercises, storage_path)

    # Calculer les completion counts pour tous les exercices
    exercises_with_progress = []
    for exercise in exercises:
        exercise_key = exercise.get("key") or str(exercise.get("id"))
        completion_count = get_exercise_completion_count(exercise_key, storage_path)
        exercises_with_progress.append(
            {**exercise, "_completion_count": completion_count}
        )

    # Définir l'ordre de difficulté
    difficulty_order = {"Débutant": 1, "Intermédiaire": 2, "Avancé": 3}

    # Trier les exercices:
    # 1. Par statut (non complétés d'abord, complétés à la fin)
    # 2. Par difficulté (Débutant, Intermédiaire, Avancé)
    # 3. Par ID croissant
    sorted_exercises = sorted(
        exercises_with_progress,
        key=lambda ex: (
            ex["_completion_count"]
            > 0,  # False (0) avant True (1) - non complétés d'abord
            difficulty_order.get(ex.get("difficulty", "Débutant"), 1),
            ex.get("id", 999),
        ),
    )

    # Créer les choix pour le menu interactif
    choices = []
    for exercise in sorted_exercises:
        # Format: "ID. [Domaine] Titre (Difficulté - Durée) [✓ complété X fois]"
        ex_id = exercise.get("id", "?")
        ex_domain = exercise.get("primary_domain", "N/A")
        ex_title = exercise.get("title", "N/A")
        ex_difficulty = exercise.get("difficulty", "N/A")
        ex_time = exercise.get("estimated_time", "N/A")
        completion_count = exercise.get("_completion_count", 0)

        # Ajouter un indicateur si complété
        status = f" [✓×{completion_count}]" if completion_count > 0 else ""
        choice_text = (
            f"{ex_id:>3}. [{ex_domain:15s}] {ex_title:45s} "
            f"({ex_difficulty:15s} - {ex_time}){status}"
        )
        choices.append(choice_text)

    choices.append("⬅️  Retour au menu principal")

    # Menu interactif
    questions = [
        inquirer.List(
            "exercise",
            message=(
                "Choisissez un exercice (↑↓ ou j/k, Entrée pour sélectionner, "
                "ESC pour quitter)"
            ),
            choices=choices,
            carousel=True,
        )
    ]

    try:
        answers = inquirer.prompt(questions)

        # Gérer ESC ou annulation (answers est None)
        if answers is None:
            console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
            return False

        if answers.get("exercise") == "⬅️  Retour au menu principal":
            console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
            return False

        # Extraire l'ID de l'exercice sélectionné
        selected_text = answers["exercise"]
        exercise_id = int(selected_text.split(".")[0].strip())

        # Trouver l'exercice correspondant dans la liste originale
        selected_exercise = None
        for exercise in sorted_exercises:
            if exercise.get("id") == exercise_id:
                selected_exercise = exercise
                break

        if selected_exercise is None:
            display_error_message(
                "Exercice introuvable",
                f"L'ID '{exercise_id}' ne correspond à aucun exercice disponible.",
            )
            return False

    except KeyboardInterrupt:
        console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
        return False

    # Récupérer le completion_count (déjà calculé lors du tri)
    completion_count = selected_exercise.get("_completion_count", 0)

    # Récupérer la clé unique de l'exercice
    exercise_key = selected_exercise.get("key") or str(selected_exercise.get("id"))

    # Afficher la progression
    if completion_count > 0:
        console.print(
            f"\n[cyan]📈 Progression: Vous avez complété cet exercice "
            f"{completion_count} fois. Difficulté automatiquement augmentée ![/cyan]\n"
        )

    # Generate or load cached exercise content
    console.print(
        f"\n[cyan]🤖 Génération de l'exercice "
        f"'{selected_exercise['title']}' (niveau {completion_count + 1})...[/cyan]"
    )

    try:
        generator = ExerciseGenerator()
        cache_dir = storage_path / "exercises_cache"

        # Cache key includes completion count for progressive difficulty
        cache_key = f"{exercise_key}_v{completion_count}"

        # Try to load from cache first
        exercise_content = generator.load_cached_exercise(cache_key, cache_dir)

        if exercise_content is None:
            # Generate new exercise with progressive difficulty
            exercise_content = generator.generate_exercise(
                topic=selected_exercise["title"],
                difficulty=selected_exercise["difficulty"],
                duration=selected_exercise["estimated_time"],
                completion_count=completion_count,
            )
            # Cache for future use
            generator.cache_exercise(cache_key, exercise_content, cache_dir)
            console.print("[green]✓ Exercice généré avec succès![/green]")
        else:
            console.print("[green]✓ Exercice chargé depuis le cache![/green]")

    except ValueError as e:
        display_error_message(
            "Erreur de génération",
            f"Impossible de générer l'exercice: {e}\n\n"
            "Vérifiez que GEMINI_API_KEY est configuré dans .env",
        )
        return False
    except Exception as e:
        display_error_message(
            "Erreur",
            f"Une erreur est survenue: {e}",
        )
        return False

    # Enregistrer la session
    record_exercise_session(selected_exercise, exercise_content, storage_path)
    return True
