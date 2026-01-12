"""Tests pour l'étape Reinforce."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.lms.steps.reinforce import (
    display_exercises_table,
    get_available_domains,
    get_available_exercises,
    get_exercise_progress,
    get_storage_path,
    record_exercise_session,
    reinforce_step,
    save_exercise_progress,
)


class TestGetStoragePath:
    """Tests pour get_storage_path()."""

    def test_returns_default_path_when_no_env_var(self, monkeypatch):
        """
        Given: Variable STORAGE_PATH non définie
        When: Appel de get_storage_path()
        Then: Retourne le chemin par défaut ~/.local/share/skillops
        """
        monkeypatch.delenv("STORAGE_PATH", raising=False)
        result = get_storage_path()
        expected = Path.home() / ".local/share/skillops"
        assert result == expected

    def test_returns_custom_path_when_env_var_set(self, monkeypatch):
        """
        Given: Variable STORAGE_PATH définie
        When: Appel de get_storage_path()
        Then: Retourne le chemin configuré
        """
        custom_path = "/tmp/custom-storage"
        monkeypatch.setenv("STORAGE_PATH", custom_path)
        result = get_storage_path()
        assert result == Path(custom_path)


class TestGetAvailableDomains:
    """Tests pour get_available_domains()."""

    def test_returns_list_of_domains(self):
        """
        Given: Aucun paramètre
        When: Appel de get_available_domains()
        Then: Retourne une liste de domaines/technologies
        """
        domains = get_available_domains()
        assert isinstance(domains, list)
        assert len(domains) > 0

    def test_returns_expected_domains(self):
        """
        Given: Aucun paramètre
        When: Appel de get_available_domains()
        Then: Retourne au minimum Linux, Docker, Terraform, Kubernetes, AWS, GitLab CI
        """
        domains = get_available_domains()
        expected_domains = ["Linux", "Docker", "Terraform", "Kubernetes", "AWS", "GitLab CI"]
        assert domains == expected_domains


class TestGetAvailableExercises:
    """Tests pour get_available_exercises()."""

    def test_returns_list_of_exercises(self):
        """
        Given: Aucun paramètre
        When: Appel de get_available_exercises()
        Then: Retourne une liste d'exercices (vide si catalogue non disponible, sinon avec exercices)
        """
        exercises = get_available_exercises()
        assert isinstance(exercises, list)
        # La liste peut être vide (si catalogue non chargé) ou avoir des exercices

        # Si des exercices existent, vérifier la structure
        if len(exercises) > 0:
            first_exercise = exercises[0]
            assert "id" in first_exercise
            assert "title" in first_exercise
            assert "difficulty" in first_exercise
            assert "estimated_time" in first_exercise

    def test_exercises_have_valid_ids(self):
        """
        Given: Liste d'exercices du catalogue
        When: Vérification des IDs
        Then: Si des exercices existent, tous les IDs sont uniques
        """
        exercises = get_available_exercises()
        
        # Si pas d'exercices, test passe (liste vide acceptable)
        if len(exercises) == 0:
            return
            
        ids = [ex["id"] for ex in exercises]
        keys = [ex.get("key") for ex in exercises]

        # Tous les IDs sont des entiers
        assert all(isinstance(id, int) and id > 0 for id in ids)

        # Tous les IDs sont uniques
        assert len(ids) == len(set(ids))
        
        # Tous les keys existent et sont des strings uniques
        assert all(isinstance(key, str) and key for key in keys)
        assert len(keys) == len(set(keys))


class TestDisplayExercisesTable:
    """Tests pour display_exercises_table()."""

    def test_displays_table_with_exercises(self):
        """
        Given: Liste d'exercices
        When: Appel de display_exercises_table()
        Then: Affiche un tableau (pas d'exception)
        """
        exercises = [
            {
                "id": "test-1",
                "title": "Test Exercise",
                "difficulty": "Easy",
                "estimated_time": "10min",
            }
        ]
        # Should not raise exception
        display_exercises_table(exercises)

    def test_displays_empty_table(self):
        """
        Given: Liste vide
        When: Appel de display_exercises_table()
        Then: Affiche un tableau vide (pas d'exception)
        """
        exercises = []
        # Should not raise exception
        display_exercises_table(exercises)


class TestSaveExerciseProgress:
    """Tests pour save_exercise_progress()."""

    def test_saves_new_exercise(self, tmp_path):
        """
        Given: Nouvel exercice à sauvegarder
        When: Appel de save_exercise_progress()
        Then: Sauvegarde l'exercice dans un fichier JSON
        """
        # Execute
        save_exercise_progress("test-id", "Test Exercise", 600, True, tmp_path)

        # Verify - check JSON file was created
        progress_file = tmp_path / "reinforce_progress.json"
        assert progress_file.exists()

        # Read and verify content
        with progress_file.open("r") as f:
            data = json.load(f)

        today = datetime.now().strftime("%Y-%m-%d")
        assert today in data
        assert len(data[today]["exercises"]) == 1
        assert data[today]["exercises"][0]["id"] == "test-id"
        assert data[today]["exercises"][0]["title"] == "Test Exercise"
        assert data[today]["exercises"][0]["duration_seconds"] == 600
        assert data[today]["exercises"][0]["completed"] is True
        assert data[today]["total_time"] == 600

    def test_updates_existing_exercise(self, tmp_path):
        """
        Given: Exercice existant à mettre à jour
        When: Appel de save_exercise_progress() avec le même ID
        Then: Met à jour l'exercice existant au lieu d'en créer un nouveau
        """
        # Setup - create initial exercise
        save_exercise_progress("test-id", "Old Title", 300, False, tmp_path)

        # Execute - update same exercise
        save_exercise_progress("test-id", "New Title", 600, True, tmp_path)

        # Verify
        progress_file = tmp_path / "reinforce_progress.json"
        with progress_file.open("r") as f:
            data = json.load(f)

        today = datetime.now().strftime("%Y-%m-%d")
        # Should still have only 1 exercise (updated, not added)
        assert len(data[today]["exercises"]) == 1
        assert data[today]["exercises"][0]["title"] == "New Title"
        assert data[today]["exercises"][0]["duration_seconds"] == 600
        assert data[today]["exercises"][0]["completed"] is True
        assert data[today]["total_time"] == 600


class TestGetExerciseProgress:
    """Tests pour get_exercise_progress()."""

    def test_returns_progress_when_found(self, tmp_path):
        """
        Given: Exercice avec progression sauvegardée
        When: Appel de get_exercise_progress()
        Then: Retourne les données de progression
        """
        # Setup - save an exercise
        save_exercise_progress("test-id", "Test Exercise", 600, True, tmp_path)

        # Execute
        result = get_exercise_progress("test-id", tmp_path)

        # Verify
        assert result is not None
        assert result["id"] == "test-id"
        assert result["title"] == "Test Exercise"
        assert result["duration_seconds"] == 600
        assert result["completed"] is True

    def test_returns_none_when_not_found(self, tmp_path):
        """
        Given: Exercice sans progression
        When: Appel de get_exercise_progress()
        Then: Retourne None
        """
        # Execute - no file exists yet
        result = get_exercise_progress("nonexistent", tmp_path)

        # Verify
        assert result is None


class TestRecordExerciseSession:
    """Tests pour record_exercise_session()."""

    @patch("src.lms.steps.reinforce.save_exercise_progress")
    @patch("src.lms.steps.reinforce.Confirm")
    @patch("src.lms.steps.reinforce.datetime")
    @patch("builtins.input", return_value="")
    def test_records_completed_exercise(
        self, mock_input, mock_datetime, mock_confirm, mock_save, tmp_path
    ):
        """
        Given: Utilisateur complète un exercice
        When: Appel de record_exercise_session()
        Then: Sauvegarde avec completed=True
        """
        # Setup
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 10, 10)  # 10 minutes plus tard

        mock_datetime.now.side_effect = [start_time, end_time]
        mock_confirm.ask.return_value = True

        exercise = {
            "id": "test-id",
            "title": "Test Exercise",
            "difficulty": "Easy",
            "estimated_time": "10min",
        }
        
        exercise_content = {
            "title": "Test Exercise",
            "instructions": "Test instructions",
            "validation": "Test validation",
        }

        # Execute
        record_exercise_session(exercise, exercise_content, tmp_path)

        # Verify
        mock_save.assert_called_once()
        call_args = mock_save.call_args[0]
        assert call_args[0] == "test-id"
        assert call_args[1] == "Test Exercise"
        assert call_args[2] == 600  # 10 minutes = 600 seconds
        assert call_args[3] is True  # completed
        assert call_args[4] == tmp_path

    @patch("src.lms.steps.reinforce.save_exercise_progress")
    @patch("src.lms.steps.reinforce.Confirm")
    @patch("src.lms.steps.reinforce.datetime")
    @patch("builtins.input", return_value="")
    def test_records_incomplete_exercise(
        self, mock_input, mock_datetime, mock_confirm, mock_save, tmp_path
    ):
        """
        Given: Utilisateur ne complète pas l'exercice
        When: Appel de record_exercise_session()
        Then: Sauvegarde avec completed=False
        """
        # Setup
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 10, 5)  # 5 minutes plus tard

        mock_datetime.now.side_effect = [start_time, end_time]
        mock_confirm.ask.return_value = False

        exercise = {
            "id": "test-id",
            "title": "Test Exercise",
            "difficulty": "Hard",
            "estimated_time": "30min",
        }
        
        exercise_content = {
            "title": "Test Exercise",
            "instructions": "Test instructions",
            "validation": "Test validation",
        }

        # Execute
        record_exercise_session(exercise, exercise_content, tmp_path)

        # Verify
        call_args = mock_save.call_args[0]
        assert call_args[2] == 300  # 5 minutes = 300 seconds
        assert call_args[3] is False  # not completed


class TestReinforceStep:
    """Tests pour reinforce_step()."""

    @patch("src.lms.steps.reinforce.get_exercise_completion_count")
    @patch("src.lms.steps.reinforce.ExerciseGenerator")
    @patch("src.lms.steps.reinforce.record_exercise_session")
    @patch("src.lms.steps.reinforce.inquirer")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_selects_and_records_exercise(
        self, mock_exercises, mock_inquirer, mock_record, mock_generator_class, mock_completion_count, tmp_path
    ):
        """
        Given: Utilisateur choisit un exercice valide
        When: Appel de reinforce_step()
        Then: Enregistre la session de l'exercice
        """
        # Setup
        mock_exercises.return_value = [
            {
                "id": 1,
                "key": "test-exercise",
                "title": "Test Exercise",
                "primary_domain": "Test",
                "difficulty": "Easy",
                "estimated_time": "10min",
            }
        ]
        # Mock inquirer prompt response
        mock_inquirer.prompt.return_value = {
            "exercise": "  1. [Test           ] Test Exercise                                          (Easy - 10min)"
        }
        mock_completion_count.return_value = 0
        
        # Mock exercise generator
        mock_generator = mock_generator_class.return_value
        mock_generator.load_cached_exercise.return_value = {
            "title": "Test Exercise",
            "objectives": "Learn testing",
            "requirements": "Complete the test",
            "success_criteria": "All tests pass"
        }

        # Execute
        reinforce_step(tmp_path)

        # Verify
        mock_record.assert_called_once()
        recorded_exercise = mock_record.call_args[0][0]
        assert recorded_exercise["id"] == 1

    @patch("src.lms.steps.reinforce.record_exercise_session")
    @patch("src.lms.steps.reinforce.inquirer")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_exits_when_user_quits(
        self, mock_exercises, mock_prompt, mock_record, tmp_path
    ):
        """
        Given: Utilisateur tape 'q' pour quitter
        When: Appel de reinforce_step()
        Then: Quitte sans enregistrer de session
        """
        # Setup
        mock_exercises.return_value = []
        mock_prompt.ask.return_value = "q"

        # Execute
        reinforce_step(tmp_path)

        # Verify
        mock_record.assert_not_called()

    @patch("src.lms.steps.reinforce.record_exercise_session")
    @patch("src.lms.steps.reinforce.inquirer")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_shows_error_for_invalid_id(
        self, mock_exercises, mock_inquirer, mock_record, tmp_path
    ):
        """
        Given: Liste vide d'exercices
        When: Appel de reinforce_step()
        Then: Affiche un message d'erreur et ne lance pas de session
        """
        # Setup
        mock_exercises.return_value = []

        # Execute
        reinforce_step(tmp_path)

        # Verify - inquirer ne devrait pas être appelé car liste vide
        mock_inquirer.prompt.assert_not_called()
        mock_record.assert_not_called()

    @patch("src.lms.steps.reinforce.get_exercise_completion_count")
    @patch("src.lms.steps.reinforce.ExerciseGenerator")
    @patch("src.lms.steps.reinforce.get_storage_path")
    @patch("src.lms.steps.reinforce.record_exercise_session")
    @patch("src.lms.steps.reinforce.inquirer")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_uses_default_storage_path_when_none(
        self, mock_exercises, mock_inquirer, mock_record, mock_storage, mock_generator_class, mock_completion_count
    ):
        """
        Given: Aucun storage_path fourni
        When: Appel de reinforce_step()
        Then: Utilise get_storage_path() pour obtenir le chemin par défaut
        """
        # Setup
        mock_exercises.return_value = [
            {
                "id": 1,
                "key": "test-exercise",
                "title": "Test",
                "primary_domain": "Test",
                "difficulty": "Easy",
                "estimated_time": "10min",
            }
        ]
        # Mock inquirer
        mock_inquirer.prompt.return_value = {
            "exercise": "  1. [Test           ] Test                                               (Easy - 10min)"
        }
        mock_storage.return_value = Path("/default/path")
        mock_completion_count.return_value = 0
        
        # Mock exercise generator
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.load_cached_exercise.return_value = None
        mock_generator.generate_exercise.return_value = {
            "title": "Test",
            "requirements": "Test requirements",
            "success_criteria": "Test criteria",
        }

        # Execute
        reinforce_step()  # No storage_path argument

        # Verify
        mock_storage.assert_called_once()
        # record_exercise_session should be called with the exercise, content, and default path


class TestExerciseProgression:
    """Tests for exercise progression tracking."""

    def test_completion_count_returns_zero_for_new_exercise(self, tmp_path):
        """Test that completion count is 0 for a new exercise."""
        from src.lms.steps.reinforce import get_exercise_completion_count

        count = get_exercise_completion_count("new-exercise", tmp_path)
        assert count == 0

    def test_completion_count_tracks_across_days(self, tmp_path):
        """Test that completion count sums all successful completions across all days."""
        from src.lms.steps.reinforce import save_exercise_progress, get_exercise_completion_count

        # Save progress on day 1
        save_exercise_progress("docker-basics", "Docker", 600, True, tmp_path)
        
        # Manually add another day's data
        progress_file = tmp_path / "reinforce_progress.json"
        with progress_file.open("r") as f:
            import json
            data = json.load(f)
        
        # Add data for another day
        data["2026-01-11"] = {
            "exercises": [
                {"id": "docker-basics", "title": "Docker", "duration_seconds": 900, "completed": True, "timestamp": "2026-01-11T10:00:00"}
            ],
            "total_time": 900
        }
        
        with progress_file.open("w") as f:
            json.dump(data, f)
        
        # Should count both completions
        count = get_exercise_completion_count("docker-basics", tmp_path)
        assert count == 2

    def test_completion_count_ignores_incomplete_exercises(self, tmp_path):
        """Test that incomplete exercises don't increase the count."""
        from src.lms.steps.reinforce import save_exercise_progress, get_exercise_completion_count

        # Save incomplete progress
        save_exercise_progress("docker-basics", "Docker", 300, False, tmp_path)
        save_exercise_progress("docker-basics", "Docker", 400, False, tmp_path)

        count = get_exercise_completion_count("docker-basics", tmp_path)
        assert count == 0
