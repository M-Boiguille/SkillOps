"""Étape Reinforce - Pratique d'exercices avec suivi de progression."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import inquirer
import yaml
from rich.console import Console
from rich.markdown import Markdown
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

console = Console()


def _load_exercises_catalog() -> List[Dict]:
    """
    Charge le catalogue des exercices depuis exercises_catalog.yaml.

    Returns:
        List[Dict]: Liste des exercices du catalogue ou liste vide si non disponible
    """
    catalog_path = Path(__file__).parent.parent / "data" / "exercises_catalog.yaml"

    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
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
    """
    Récupère le chemin de stockage depuis l'environnement ou utilise le défaut.

    Returns:
        Path: Chemin absolu vers le répertoire de stockage
    """
    storage_path_str = os.getenv(
        "STORAGE_PATH", str(Path.home() / ".local/share/skillops")
    )
    return Path(storage_path_str).expanduser().absolute()


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
    progress_file = storage_path / "reinforce_progress.json"
    if not progress_file.exists():
        return 0

    try:
        with progress_file.open("r") as f:
            data = json.load(f)

        # Compter sur TOUS les jours (pas juste aujourd'hui)
        count = 0
        for date, day_data in data.items():
            exercises = day_data.get("exercises", [])
            for exercise in exercises:
                if exercise.get("id") == exercise_id and exercise.get("completed", False):
                    count += 1

        return count
    except (json.JSONDecodeError, OSError):
        return 0


def get_exercise_progress(exercise_id: str, storage_path: Path) -> Optional[Dict]:
    """
    Récupère la progression d'un exercice depuis le stockage.

    Args:
        exercise_id: Identifiant de l'exercice
        storage_path: Chemin vers le répertoire de stockage

    Returns:
        Optional[Dict]: Données de progression ou None si non trouvé
    """
    progress_file = storage_path / "reinforce_progress.json"
    if not progress_file.exists():
        return None

    try:
        with progress_file.open("r") as f:
            data = json.load(f)
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = data.get(today, {})
        exercises = today_data.get("exercises", [])
        for exercise in exercises:
            if exercise.get("id") == exercise_id:
                return exercise
    except (json.JSONDecodeError, OSError):
        return None

    return None


def save_exercise_progress(
    exercise_id: str,
    title: str,
    duration_seconds: int,
    completed: bool,
    storage_path: Path,
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
    storage_path.mkdir(parents=True, exist_ok=True)
    progress_file = storage_path / "reinforce_progress.json"

    # Charger les données existantes
    if progress_file.exists():
        try:
            with progress_file.open("r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}

    today = datetime.now().strftime("%Y-%m-%d")

    # Initialiser les données du jour
    if today not in data:
        data[today] = {"exercises": [], "total_time": 0}

    # Vérifier si l'exercice existe déjà
    exercises = data[today]["exercises"]
    existing_exercise = None
    for i, ex in enumerate(exercises):
        if ex.get("id") == exercise_id:
            existing_exercise = i
            break

    exercise_data = {
        "id": exercise_id,
        "title": title,
        "duration_seconds": duration_seconds,
        "completed": completed,
        "timestamp": datetime.now().isoformat(),
    }

    if existing_exercise is not None:
        exercises[existing_exercise] = exercise_data
    else:
        exercises.append(exercise_data)

    # Mettre à jour le temps total
    data[today]["total_time"] = sum(ex["duration_seconds"] for ex in exercises)

    # Sauvegarder
    with progress_file.open("w") as f:
        json.dump(data, f, indent=2)


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
    console.print("\n[bold yellow]✅ Critères de réussite (auto-évaluation):[/bold yellow]")
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

    console.print("\n[cyan]⏱️  Chronomètre démarré ! Appuyez sur Entrée quand "
                  "vous avez terminé...[/cyan]")
    start_time = datetime.now()
    input()  # Attendre que l'utilisateur appuie sur Entrée

    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    # Auto-évaluation basée sur les critères de succès
    console.print("\n[bold cyan]📊 Auto-évaluation[/bold cyan]")
    console.print("\nRevisez les critères de réussite ci-dessus.")
    console.print("Avez-vous validé TOUS les critères ?\n")

    completed = Confirm.ask(
        "✅ J'ai vérifié et validé tous les critères de succès", default=False
    )

    # Sauvegarder la progression
    save_exercise_progress(
        exercise["id"],
        exercise["title"],
        duration,
        completed,
        storage_path,
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


def reinforce_step(storage_path: Optional[Path] = None) -> None:
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
        return

    # Calculer les completion counts pour tous les exercices
    exercises_with_progress = []
    for exercise in exercises:
        exercise_key = exercise.get("key") or str(exercise.get("id"))
        completion_count = get_exercise_completion_count(exercise_key, storage_path)
        exercises_with_progress.append({
            **exercise,
            '_completion_count': completion_count
        })

    # Définir l'ordre de difficulté
    difficulty_order = {
        'Débutant': 1,
        'Intermédiaire': 2,
        'Avancé': 3
    }

    # Trier les exercices:
    # 1. Par statut (non complétés d'abord, complétés à la fin)
    # 2. Par difficulté (Débutant, Intermédiaire, Avancé)
    # 3. Par ID croissant
    sorted_exercises = sorted(
        exercises_with_progress,
        key=lambda ex: (
            ex['_completion_count'] > 0,  # False (0) avant True (1) - non complétés d'abord
            difficulty_order.get(ex.get('difficulty', 'Débutant'), 1),
            ex.get('id', 999)
        )
    )

    # Créer les choix pour le menu interactif
    choices = []
    for exercise in sorted_exercises:
        # Format: "ID. [Domaine] Titre (Difficulté - Durée) [✓ complété X fois]"
        ex_id = exercise.get('id', '?')
        ex_domain = exercise.get('primary_domain', 'N/A')
        ex_title = exercise.get('title', 'N/A')
        ex_difficulty = exercise.get('difficulty', 'N/A')
        ex_time = exercise.get('estimated_time', 'N/A')
        completion_count = exercise.get('_completion_count', 0)

        # Ajouter un indicateur si complété
        status = f" [✓×{completion_count}]" if completion_count > 0 else ""
        choice_text = f"{ex_id:>3}. [{ex_domain:15s}] {ex_title:45s} ({ex_difficulty:15s} - {ex_time}){status}"
        choices.append(choice_text)

    choices.append("⬅️  Retour au menu principal")

    # Menu interactif
    questions = [
        inquirer.List(
            "exercise",
            message="Choisissez un exercice (↑↓ ou j/k, Entrée pour sélectionner, ESC pour quitter)",
            choices=choices,
            carousel=True,
        )
    ]

    try:
        answers = inquirer.prompt(questions)

        # Gérer ESC ou annulation (answers est None)
        if answers is None:
            console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
            return

        if answers.get("exercise") == "⬅️  Retour au menu principal":
            console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
            return

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
            return

    except KeyboardInterrupt:
        console.print("\n[yellow]Retour au menu principal...[/yellow]\n")
        return

    # Récupérer le completion_count (déjà calculé lors du tri)
    completion_count = selected_exercise.get('_completion_count', 0)

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
        return
    except Exception as e:
        display_error_message(
            "Erreur",
            f"Une erreur est survenue: {e}",
        )
        return

    # Enregistrer la session
    record_exercise_session(selected_exercise, exercise_content, storage_path)
