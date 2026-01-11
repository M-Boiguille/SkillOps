"""Tests pour l'étape Reinforce."""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
from rich.table import Table

from src.lms.steps.reinforce import (
    display_exercises_table,
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


class TestGetAvailableExercises:
    """Tests pour get_available_exercises()."""

    def test_returns_list_of_exercises(self):
        """
        Given: Aucun paramètre
        When: Appel de get_available_exercises()
        Then: Retourne une liste d'exercices avec id, titre, difficulté, durée
        """
        exercises = get_available_exercises()
        assert isinstance(exercises, list)
        assert len(exercises) > 0

        # Vérifier la structure du premier exercice
        first_exercise = exercises[0]
        assert "id" in first_exercise
        assert "title" in first_exercise
        assert "difficulty" in first_exercise
        assert "estimated_time" in first_exercise

    def test_exercises_have_valid_ids(self):
        """
        Given: Liste d'exercices
        When: Vérification des IDs
        Then: Tous les IDs sont des strings non-vides et uniques
        """
        exercises = get_available_exercises()
        ids = [ex["id"] for ex in exercises]

        # Tous les IDs sont des strings non-vides
        assert all(isinstance(id, str) and id for id in ids)

        # Tous les IDs sont uniques
        assert len(ids) == len(set(ids))


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

    @patch("src.lms.steps.reinforce.ProgressManager")
    def test_saves_new_exercise(self, mock_pm_class, tmp_path):
        """
        Given: Nouvel exercice à sauvegarder
        When: Appel de save_exercise_progress()
        Then: Sauvegarde l'exercice avec les bonnes données
        """
        # Setup
        mock_pm = MagicMock()
        mock_pm_class.return_value = mock_pm
        mock_pm.load.return_value = None  # Pas de progression existante

        # Execute
        save_exercise_progress("test-id", "Test Exercise", 600, True, tmp_path)

        # Verify
        mock_pm.save.assert_called_once()
        call_args = mock_pm.save.call_args
        # date should be today's date in YYYY-MM-DD format
        assert isinstance(call_args[0][0], str)
        progress = call_args[0][1]  # progress data

        assert "reinforce" in progress
        assert len(progress["reinforce"]["exercises"]) == 1
        assert progress["reinforce"]["exercises"][0]["id"] == "test-id"
        assert progress["reinforce"]["exercises"][0]["completed"] is True
        assert progress["reinforce"]["total_time"] == 600

    @patch("src.lms.steps.reinforce.ProgressManager")
    def test_updates_existing_exercise(self, mock_pm_class, tmp_path):
        """
        Given: Exercice existant à mettre à jour
        When: Appel de save_exercise_progress() avec le même ID
        Then: Met à jour l'exercice existant au lieu d'en créer un nouveau
        """
        # Setup
        mock_pm = MagicMock()
        mock_pm_class.return_value = mock_pm
        mock_pm.load.return_value = {
            "reinforce": {
                "exercises": [
                    {
                        "id": "test-id",
                        "title": "Old Title",
                        "duration_seconds": 300,
                        "completed": False,
                        "timestamp": "2024-01-15T09:00:00",
                    }
                ],
                "total_time": 300,
            }
        }

        # Execute
        save_exercise_progress("test-id", "New Title", 600, True, tmp_path)

        # Verify
        call_args = mock_pm.save.call_args
        progress = call_args[0][1]

        # Should still have only 1 exercise (updated, not added)
        assert len(progress["reinforce"]["exercises"]) == 1
        assert progress["reinforce"]["exercises"][0]["title"] == "New Title"
        assert progress["reinforce"]["exercises"][0]["duration_seconds"] == 600
        assert progress["reinforce"]["exercises"][0]["completed"] is True
        assert progress["reinforce"]["total_time"] == 600


class TestGetExerciseProgress:
    """Tests pour get_exercise_progress()."""

    @patch("src.lms.steps.reinforce.ProgressManager")
    def test_returns_progress_when_found(self, mock_pm_class, tmp_path):
        """
        Given: Exercice avec progression sauvegardée
        When: Appel de get_exercise_progress()
        Then: Retourne les données de progression
        """
        # Setup
        mock_pm = MagicMock()
        mock_pm_class.return_value = mock_pm
        mock_pm.load.return_value = {
            "reinforce": {
                "exercises": [
                    {
                        "id": "test-id",
                        "title": "Test Exercise",
                        "duration_seconds": 600,
                        "completed": True,
                    }
                ]
            }
        }

        # Execute
        result = get_exercise_progress("test-id", tmp_path)

        # Verify
        assert result is not None
        assert result["id"] == "test-id"
        assert result["completed"] is True

    @patch("src.lms.steps.reinforce.ProgressManager")
    def test_returns_none_when_not_found(self, mock_pm_class, tmp_path):
        """
        Given: Exercice sans progression
        When: Appel de get_exercise_progress()
        Then: Retourne None
        """
        # Setup
        mock_pm = MagicMock()
        mock_pm_class.return_value = mock_pm
        mock_pm.load.return_value = None

        # Execute
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

        # Execute
        record_exercise_session(exercise, tmp_path)

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

        # Execute
        record_exercise_session(exercise, tmp_path)

        # Verify
        call_args = mock_save.call_args[0]
        assert call_args[2] == 300  # 5 minutes = 300 seconds
        assert call_args[3] is False  # not completed


class TestReinforceStep:
    """Tests pour reinforce_step()."""

    @patch("src.lms.steps.reinforce.record_exercise_session")
    @patch("src.lms.steps.reinforce.Prompt")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_selects_and_records_exercise(
        self, mock_exercises, mock_prompt, mock_record, tmp_path
    ):
        """
        Given: Utilisateur choisit un exercice valide
        When: Appel de reinforce_step()
        Then: Enregistre la session de l'exercice
        """
        # Setup
        mock_exercises.return_value = [
            {
                "id": "test-1",
                "title": "Test Exercise",
                "difficulty": "Easy",
                "estimated_time": "10min",
            }
        ]
        mock_prompt.ask.return_value = "test-1"

        # Execute
        reinforce_step(tmp_path)

        # Verify
        mock_record.assert_called_once()
        recorded_exercise = mock_record.call_args[0][0]
        assert recorded_exercise["id"] == "test-1"

    @patch("src.lms.steps.reinforce.record_exercise_session")
    @patch("src.lms.steps.reinforce.Prompt")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_exits_when_user_quits(self, mock_exercises, mock_prompt, mock_record, tmp_path):
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
    @patch("src.lms.steps.reinforce.Prompt")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_shows_error_for_invalid_id(
        self, mock_exercises, mock_prompt, mock_record, tmp_path
    ):
        """
        Given: Utilisateur entre un ID invalide
        When: Appel de reinforce_step()
        Then: Affiche un message d'erreur et ne lance pas de session
        """
        # Setup
        mock_exercises.return_value = [
            {"id": "test-1", "title": "Test", "difficulty": "Easy", "estimated_time": "10min"}
        ]
        mock_prompt.ask.return_value = "invalid-id"

        # Execute
        reinforce_step(tmp_path)

        # Verify
        mock_record.assert_not_called()

    @patch("src.lms.steps.reinforce.get_storage_path")
    @patch("src.lms.steps.reinforce.record_exercise_session")
    @patch("src.lms.steps.reinforce.Prompt")
    @patch("src.lms.steps.reinforce.get_available_exercises")
    def test_uses_default_storage_path_when_none(
        self, mock_exercises, mock_prompt, mock_record, mock_storage
    ):
        """
        Given: Aucun storage_path fourni
        When: Appel de reinforce_step()
        Then: Utilise get_storage_path() pour obtenir le chemin par défaut
        """
        # Setup
        mock_exercises.return_value = [
            {"id": "test-1", "title": "Test", "difficulty": "Easy", "estimated_time": "10min"}
        ]
        mock_prompt.ask.return_value = "test-1"
        mock_storage.return_value = Path("/default/path")

        # Execute
        reinforce_step()  # No storage_path argument

        # Verify
        mock_storage.assert_called_once()
        # record_exercise_session should be called with the default path
        assert mock_record.call_args[0][1] == Path("/default/path")
