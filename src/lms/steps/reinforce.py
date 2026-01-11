"""Étape Reinforce - Pratique d'exercices avec suivi de progression."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..display import (
    display_error_message,
    display_info_panel,
    display_section_header,
    display_success_message,
    format_time_duration,
)
from ..persistence import ProgressManager

console = Console()


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


def get_available_exercises() -> List[Dict[str, str]]:
    """
    Retourne la liste des exercices disponibles.

    Returns:
        List[Dict]: Liste des exercices avec id, titre, difficulté, durée estimée
    """
    return [
        {
            "id": "docker-basics",
            "title": "Docker Basics - Créer et gérer des conteneurs",
            "difficulty": "Débutant",
            "estimated_time": "15min",
        },
        {
            "id": "k8s-pods",
            "title": "Kubernetes - Déploiement de Pods",
            "difficulty": "Intermédiaire",
            "estimated_time": "30min",
        },
        {
            "id": "terraform-aws",
            "title": "Terraform - Infrastructure AWS",
            "difficulty": "Intermédiaire",
            "estimated_time": "45min",
        },
        {
            "id": "ansible-playbook",
            "title": "Ansible - Configuration automatisée",
            "difficulty": "Débutant",
            "estimated_time": "20min",
        },
        {
            "id": "cicd-pipeline",
            "title": "CI/CD - Pipeline GitHub Actions",
            "difficulty": "Avancé",
            "estimated_time": "60min",
        },
    ]


def display_exercises_table(exercises: List[Dict[str, str]]) -> None:
    """
    Affiche un tableau des exercices disponibles.

    Args:
        exercises: Liste des exercices à afficher
    """
    table = Table(
        title="📝 Exercices disponibles", show_header=True, header_style="bold cyan"
    )
    table.add_column("ID", style="cyan", width=20)
    table.add_column("Titre", style="white", width=40)
    table.add_column("Difficulté", style="yellow", width=15)
    table.add_column("Durée", style="green", width=10)

    for exercise in exercises:
        table.add_row(
            exercise["id"],
            exercise["title"],
            exercise["difficulty"],
            exercise["estimated_time"],
        )

    console.print()
    console.print(table)
    console.print()


def get_exercise_progress(exercise_id: str, storage_path: Path) -> Optional[Dict]:
    """
    Récupère la progression d'un exercice depuis le stockage.

    Args:
        exercise_id: Identifiant de l'exercice
        storage_path: Chemin vers le répertoire de stockage

    Returns:
        Optional[Dict]: Données de progression ou None si non trouvé
    """
    progress_manager = ProgressManager(storage_path)
    today = datetime.now().strftime("%Y-%m-%d")
    today_progress = progress_manager.load(today)

    if today_progress and "reinforce" in today_progress:
        exercises = today_progress["reinforce"].get("exercises", [])
        for exercise in exercises:
            if exercise.get("id") == exercise_id:
                return exercise

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
    progress_manager = ProgressManager(storage_path)
    today = datetime.now().strftime("%Y-%m-%d")

    # Charger la progression existante
    progress = progress_manager.load(today) or {}

    # Initialiser reinforce s'il n'existe pas
    if "reinforce" not in progress:
        progress["reinforce"] = {"exercises": [], "total_time": 0}

    # Vérifier si l'exercice existe déjà
    exercises = progress["reinforce"]["exercises"]
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
        # Mettre à jour l'exercice existant
        exercises[existing_exercise] = exercise_data
    else:
        # Ajouter un nouvel exercice
        exercises.append(exercise_data)

    # Mettre à jour le temps total
    progress["reinforce"]["total_time"] = sum(
        ex["duration_seconds"] for ex in exercises
    )

    # Sauvegarder
    progress_manager.save(today, progress)


def record_exercise_session(exercise: Dict[str, str], storage_path: Path) -> None:
    """
    Enregistre une session d'exercice avec chronomètre et validation.

    Args:
        exercise: Dictionnaire avec les données de l'exercice
        storage_path: Chemin vers le répertoire de stockage
    """
    display_info_panel(
        f"Exercice : {exercise['title']}",
        f"Difficulté : {exercise['difficulty']}\n"
        f"Durée estimée : {exercise['estimated_time']}",
    )

    console.print(
        "\n[cyan]Appuyez sur Entrée quand vous avez terminé l'exercice...[/cyan]"
    )
    start_time = datetime.now()
    input()  # Attendre que l'utilisateur appuie sur Entrée

    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    # Demander si l'exercice est terminé
    completed = Confirm.ask(
        "\n✅ Avez-vous terminé l'exercice avec succès ?", default=True
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
    3. Enregistre la session avec chronomètre
    4. Sauvegarde la progression

    Args:
        storage_path: Chemin vers le répertoire de stockage (optionnel)
    """
    display_section_header("Reinforce - Pratique", "💪")

    # Déterminer le chemin de stockage
    if storage_path is None:
        storage_path = get_storage_path()

    # Récupérer les exercices disponibles
    exercises = get_available_exercises()

    # Afficher le tableau
    display_exercises_table(exercises)

    # Demander à l'utilisateur de choisir un exercice
    console.print(
        "[cyan]Choisissez un exercice en entrant son ID (ou 'q' pour quitter) :[/cyan]"
    )
    exercise_id = Prompt.ask("ID de l'exercice")

    if exercise_id.lower() == "q":
        console.print("\n[yellow]À bientôt ! 👋[/yellow]\n")
        return

    # Trouver l'exercice sélectionné
    selected_exercise = None
    for exercise in exercises:
        if exercise["id"] == exercise_id:
            selected_exercise = exercise
            break

    if selected_exercise is None:
        display_error_message(
            "Exercice introuvable",
            f"L'ID '{exercise_id}' ne correspond à aucun exercice disponible.",
        )
        return

    # Enregistrer la session
    record_exercise_session(selected_exercise, storage_path)
