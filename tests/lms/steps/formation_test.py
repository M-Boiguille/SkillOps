"""Tests pour l'étape Formation (Active Recall)."""

from unittest.mock import patch
from src.lms.steps.formation import formation_step, _save_session_log


class TestFormationStep:
    """Tests pour le workflow formation_step."""

    @patch("src.lms.steps.formation.Prompt")
    @patch("src.lms.steps.formation._save_session_log")
    @patch("src.lms.steps.formation.console")
    def test_formation_step_full_flow(self, mock_console, mock_save, mock_prompt):
        """Test le flux complet : Priming -> Wait -> Exit Ticket."""
        # Mocks
        # 1. Priming: 3 objectifs (2 remplis, 1 vide pour stop)
        # 2. Wait session (Enter)
        # 3. Exit Ticket (Recall)
        mock_prompt.ask.side_effect = [
            "Objectif 1",
            "Objectif 2",
            "",  # Priming loop
            "",  # Session wait
            "Ceci est un résumé valide de plus de 10 caractères.",  # Recall
        ]

        formation_step()

        # Vérifier que save a été appelé avec les bonnes données
        mock_save.assert_called_once()
        args = mock_save.call_args[0]
        assert args[0] == ["Objectif 1", "Objectif 2"]
        assert "Ceci est un résumé" in args[1]
        assert isinstance(args[2], int)  # duration

    @patch("src.lms.steps.formation.Prompt")
    @patch("src.lms.steps.formation.console")
    def test_formation_step_no_goals(self, mock_console, mock_prompt):
        """Test arrêt si aucun objectif défini."""
        mock_prompt.ask.return_value = ""  # Vide direct

        formation_step()

        # Doit afficher un message d'erreur
        assert any(
            "Il faut au moins un objectif" in str(c)
            for c in mock_console.print.call_args_list
        )


class TestSaveSessionLog:
    """Tests pour la persistance du journal."""

    @patch("src.lms.steps.formation.save_formation_log")
    def test_save_session_log_calls_persistence(self, mock_save_log):
        """Test que la fonction de persistance est appelée."""
        _save_session_log(["Goal 1"], "Recall text", 45)

        mock_save_log.assert_called_once_with(
            ["Goal 1"], "Recall text", 45, wakatime_minutes=0
        )
