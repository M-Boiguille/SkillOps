"""Tests end-to-end pour le CLI SkillOps.

Ces tests vérifient l'intégration complète du CLI, incluant le menu principal,
la navigation entre les étapes, et l'exécution des commandes Typer.
"""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from src.lms.cli import STEPS, Step, execute_step, main_menu
from src.lms.main import app

runner = CliRunner()


class TestCliCommands:
    """Tests pour les commandes Typer du CLI."""

    def test_version_command(self):
        """
        Given: Application Typer configurée
        When: Exécution de la commande 'version'
        Then: Affiche la version du LMS
        """
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "SkillOps LMS" in result.stdout
        assert "0.2.0" in result.stdout

    @patch("src.lms.main.main_menu")
    @patch("src.lms.main.execute_step")
    def test_start_command_with_quit(self, mock_execute, mock_menu):
        """
        Given: Menu qui retourne None (quit)
        When: Exécution de la commande 'start'
        Then: Quitte le programme
        """
        mock_menu.return_value = None

        result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        mock_menu.assert_called_once()
        mock_execute.assert_not_called()

    @patch("src.lms.main.main_menu")
    @patch("src.lms.main.execute_step")
    def test_start_command_executes_step(self, mock_execute, mock_menu):
        """
        Given: Menu qui retourne une étape puis None
        When: Exécution de la commande 'start'
        Then: Exécute l'étape puis quitte
        """
        test_step = Step(1, "Test Step", "🧪", False)
        mock_menu.side_effect = [test_step, None]

        result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert mock_menu.call_count == 2
        mock_execute.assert_called_once_with(test_step)

    @patch("src.lms.main.main_menu")
    @patch("src.lms.main.execute_step")
    def test_start_command_handles_multiple_steps(self, mock_execute, mock_menu):
        """
        Given: Menu qui retourne plusieurs étapes puis None
        When: Exécution de la commande 'start'
        Then: Exécute toutes les étapes dans l'ordre
        """
        step1 = Step(1, "Step 1", "1️⃣", False)
        step2 = Step(2, "Step 2", "2️⃣", False)
        step3 = Step(3, "Step 3", "3️⃣", False)
        mock_menu.side_effect = [step1, step2, step3, None]

        result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert mock_menu.call_count == 4
        assert mock_execute.call_count == 3
        mock_execute.assert_any_call(step1)
        mock_execute.assert_any_call(step2)
        mock_execute.assert_any_call(step3)


class TestMainMenuIntegration:
    """Tests d'intégration pour main_menu()."""

    @patch("src.lms.cli.inquirer.prompt")
    def test_menu_returns_selected_step(self, mock_prompt):
        """
        Given: Utilisateur sélectionne une étape valide
        When: Appel de main_menu()
        Then: Retourne l'objet Step correspondant
        """
        # Simuler la sélection de la première étape
        mock_prompt.return_value = {"step": "1. 📊 Review"}

        result = main_menu()

        assert result is not None
        assert isinstance(result, Step)
        assert result.number == 1
        assert result.name == "Review"

    @patch("src.lms.cli.inquirer.prompt")
    def test_menu_returns_none_on_quit(self, mock_prompt):
        """
        Given: Utilisateur sélectionne 'Exit'
        When: Appel de main_menu()
        Then: Retourne None
        """
        mock_prompt.return_value = {"step": "❌ Exit"}

        result = main_menu()

        assert result is None

    @patch("src.lms.cli.inquirer.prompt")
    def test_menu_handles_keyboard_interrupt(self, mock_prompt):
        """
        Given: Utilisateur interrompt avec Ctrl+C
        When: Appel de main_menu()
        Then: Retourne None gracieusement
        """
        mock_prompt.side_effect = KeyboardInterrupt()

        result = main_menu()

        assert result is None

    @patch("src.lms.cli.inquirer.prompt")
    def test_menu_returns_correct_step_for_each_option(self, mock_prompt):
        """
        Given: Chaque option du menu sélectionnée
        When: Appel de main_menu()
        Then: Retourne le bon Step correspondant
        """
        # Tester chaque étape
        for i, step in enumerate(STEPS, start=1):
            choice = f"{i}. {step.emoji} {step.name}"
            mock_prompt.return_value = {"step": choice}

            result = main_menu()

            assert result is not None
            assert result.number == step.number
            assert result.name == step.name
            assert result.emoji == step.emoji


class TestExecuteStepIntegration:
    """Tests d'intégration pour execute_step()."""

    @patch("src.lms.cli.console.print")
    def test_execute_step_displays_step_info(self, mock_print):
        """
        Given: Un Step à exécuter
        When: Appel de execute_step()
        Then: Affiche les informations de l'étape
        """
        test_step = Step(1, "Test Step", "🧪", False)

        execute_step(test_step)

        # Vérifier qu'on a affiché quelque chose
        assert mock_print.called

    @patch("src.lms.cli.console.print")
    def test_execute_step_with_all_steps(self, mock_print):
        """
        Given: Toutes les étapes du workflow
        When: Exécution de chaque étape
        Then: Aucune exception levée
        """
        for step in STEPS:
            execute_step(step)
            assert mock_print.called


class TestEndToEndWorkflow:
    """Tests de workflow complet end-to-end."""

    @patch("src.lms.cli.inquirer.prompt")
    @patch("src.lms.cli.console.print")
    def test_complete_workflow_review_then_quit(self, mock_print, mock_prompt):
        """
        Given: Workflow complet (Review → Quit)
        When: Navigation dans le menu
        Then: Exécute Review puis quitte proprement
        """
        # Premier appel : sélectionner Review
        # Deuxième appel : quitter
        mock_prompt.side_effect = [
            {"step": "1. 📊 Review"},
            {"step": "❌ Exit"},
        ]

        # Simuler le workflow
        step1 = main_menu()
        assert step1 is not None
        assert step1.name == "Review"
        execute_step(step1)

        step2 = main_menu()
        assert step2 is None

    @patch("src.lms.cli.inquirer.prompt")
    @patch("src.lms.cli.console.print")
    def test_complete_workflow_multiple_steps(self, mock_print, mock_prompt):
        """
        Given: Workflow avec 3 étapes (Review → Formation → Reinforce → Quit)
        When: Navigation dans le menu
        Then: Exécute chaque étape dans l'ordre
        """
        mock_prompt.side_effect = [
            {"step": "1. 📊 Review"},
            {"step": "2. 📚 Formation"},
            {"step": "6. 💪 Reinforce"},
            {"step": "❌ Exit"},
        ]

        # Exécuter le workflow
        steps_executed = []

        for _ in range(4):  # 3 steps + 1 quit
            step = main_menu()
            if step is None:
                break
            steps_executed.append(step.name)
            execute_step(step)

        assert steps_executed == ["Review", "Formation", "Reinforce"]

    @patch("src.lms.main.main_menu")
    @patch("src.lms.main.execute_step")
    def test_typer_app_integration(self, mock_execute, mock_menu):
        """
        Given: Application Typer complète
        When: Exécution via CliRunner
        Then: Intégration complète fonctionne
        """
        step1 = Step(1, "Review", "📊", False)
        step2 = Step(2, "Formation", "📚", False)
        mock_menu.side_effect = [step1, step2, None]

        result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        assert mock_menu.call_count == 3
        assert mock_execute.call_count == 2


class TestCliErrorHandling:
    """Tests de gestion d'erreurs du CLI."""

    @patch("src.lms.cli.inquirer.prompt")
    def test_menu_handles_empty_response(self, mock_prompt):
        """
        Given: Réponse vide (inquirer.prompt retourne None)
        When: Appel de main_menu()
        Then: Retourne None gracieusement
        """
        mock_prompt.return_value = None

        # Should not crash
        result = main_menu()
        assert result is None

    @patch("src.lms.cli.inquirer.prompt")
    def test_menu_handles_invalid_response(self, mock_prompt):
        """
        Given: Réponse invalide (pas de numéro de step)
        When: Appel de main_menu()
        Then: Lève une exception ou retourne None
        """
        mock_prompt.return_value = {"step": "Invalid Option"}

        # Le code actuel va lever ValueError lors du int()
        # C'est acceptable pour un cas invalide qui ne devrait pas arriver
        with pytest.raises(ValueError):
            main_menu()

    @patch("src.lms.main.main_menu")
    @patch("src.lms.main.execute_step")
    def test_app_handles_execute_step_exception(self, mock_execute, mock_menu):
        """
        Given: execute_step() lève une exception
        When: Exécution de l'app
        Then: L'exception est propagée (pour débogage)
        """
        step = Step(1, "Test", "🧪", False)
        mock_menu.side_effect = [step, None]
        mock_execute.side_effect = RuntimeError("Test error")

        result = runner.invoke(app, ["start"])

        # L'exception devrait être propagée
        assert result.exit_code != 0


class TestStepDataIntegrity:
    """Tests pour vérifier l'intégrité des données STEPS."""

    def test_all_steps_have_unique_numbers(self):
        """
        Given: Liste STEPS
        When: Vérification des numéros
        Then: Tous les numéros sont uniques
        """
        numbers = [step.number for step in STEPS]
        assert len(numbers) == len(set(numbers))

    def test_all_steps_have_required_fields(self):
        """
        Given: Liste STEPS
        When: Vérification des champs
        Then: Tous les steps ont number, name, emoji
        """
        for step in STEPS:
            assert isinstance(step.number, int)
            assert isinstance(step.name, str)
            assert isinstance(step.emoji, str)
            assert isinstance(step.completed, bool)
            assert step.number > 0
            assert len(step.name) > 0
            assert len(step.emoji) > 0

    def test_steps_are_sequential(self):
        """
        Given: Liste STEPS
        When: Vérification de l'ordre
        Then: Les numéros sont séquentiels (1, 2, 3, ...)
        """
        numbers = [step.number for step in STEPS]
        expected = list(range(1, len(STEPS) + 1))
        assert numbers == expected
