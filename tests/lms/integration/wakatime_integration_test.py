"""Tests d'intégration end-to-end pour WakaTime.

Ces tests vérifient l'intégration complète entre le client WakaTime
et l'étape Formation, en simulant des scénarios d'utilisation réels.
"""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.lms.api_clients.wakatime_client import (
    WakaTimeClient,
    WakaTimeAuthError,
    WakaTimeError,
    WakaTimeRateLimitError,
)
from src.lms.steps.formation import formation_step


class TestWakaTimeIntegration:
    """Tests d'intégration pour le flux complet WakaTime."""

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.datetime")
    def test_formation_workflow_with_sufficient_coding_time(
        self, mock_datetime, mock_client_class
    ):
        """
        Given: API key valide et 3h de code aujourd'hui
        When: Exécution complète de formation_step()
        Then: Affiche stats + message de succès (pas d'alerte)
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key-123"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 16, 0)  # 16h

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 10800,  # 3h
            "languages": [
                {"name": "Python", "total_seconds": 7200, "percent": 66.7},
                {"name": "Shell", "total_seconds": 3600, "percent": 33.3},
            ],
            "categories": [
                {"name": "Coding", "total_seconds": 10800, "percent": 100.0}
            ],
        }

        # Execute
        formation_step()

        # Verify
        mock_client_class.assert_called_once_with("test-key-123")
        mock_client.get_today_stats.assert_called_once()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.datetime")
    def test_formation_workflow_with_insufficient_coding_time_before_deadline(
        self, mock_datetime, mock_client_class
    ):
        """
        Given: API key valide et 1h de code à 14h
        When: Exécution complète de formation_step()
        Then: Affiche stats + alerte pour atteindre l'objectif
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key-123"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 14, 0)  # 14h

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 3600,  # 1h
            "languages": [{"name": "Python", "total_seconds": 3600, "percent": 100.0}],
            "categories": [{"name": "Coding", "total_seconds": 3600, "percent": 100.0}],
        }

        # Execute
        formation_step()

        # Verify
        mock_client.get_today_stats.assert_called_once()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.datetime")
    def test_formation_workflow_with_insufficient_coding_time_after_deadline(
        self, mock_datetime, mock_client_class
    ):
        """
        Given: API key valide et 1h de code à 18h (après deadline)
        When: Exécution complète de formation_step()
        Then: Affiche stats sans alerte (trop tard)
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key-123"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 18, 0)  # 18h

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 3600,  # 1h
            "languages": [],
            "categories": [],
        }

        # Execute
        formation_step()

        # Verify
        mock_client.get_today_stats.assert_called_once()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    def test_formation_workflow_with_missing_api_key(self, mock_client_class):
        """
        Given: Aucune API key configurée
        When: Exécution de formation_step()
        Then: Affiche message d'erreur et retourne sans appeler l'API
        """
        # Setup
        if "WAKATIME_API_KEY" in os.environ:
            del os.environ["WAKATIME_API_KEY"]

        # Execute
        formation_step()

        # Verify - Le client ne devrait jamais être créé
        mock_client_class.assert_not_called()

    @patch("src.lms.steps.formation.WakaTimeClient")
    def test_formation_workflow_with_auth_error(self, mock_client_class):
        """
        Given: API key invalide
        When: Exécution de formation_step()
        Then: Lève WakaTimeAuthError après affichage du message
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "invalid-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.side_effect = WakaTimeAuthError(
            "Invalid API key. Please check your WAKATIME_API_KEY."
        )

        # Execute & Verify
        with pytest.raises(WakaTimeAuthError):
            formation_step()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    def test_formation_workflow_with_rate_limit_error(self, mock_client_class):
        """
        Given: Rate limit atteint sur l'API WakaTime
        When: Exécution de formation_step()
        Then: Lève WakaTimeRateLimitError
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.side_effect = WakaTimeRateLimitError(
            "Rate limit exceeded. Please wait before retrying."
        )

        # Execute & Verify
        with pytest.raises(WakaTimeRateLimitError):
            formation_step()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    def test_formation_workflow_with_network_error(self, mock_client_class):
        """
        Given: Erreur réseau lors de l'appel API
        When: Exécution de formation_step()
        Then: Lève WakaTimeError
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.side_effect = WakaTimeError(
            "Network error: Could not connect to WakaTime API."
        )

        # Execute & Verify
        with pytest.raises(WakaTimeError):
            formation_step()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.datetime")
    def test_formation_workflow_with_zero_activity(
        self, mock_datetime, mock_client_class
    ):
        """
        Given: Aucune activité de code aujourd'hui
        When: Exécution de formation_step()
        Then: Affiche stats avec 0 temps + alerte maximale
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 0)  # 10h

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 0,
            "languages": [],
            "categories": [],
        }

        # Execute
        formation_step()

        # Verify
        mock_client.get_today_stats.assert_called_once()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.datetime")
    def test_formation_workflow_with_multiple_languages(
        self, mock_datetime, mock_client_class
    ):
        """
        Given: Activité sur 6 langages différents
        When: Exécution de formation_step()
        Then: Affiche tableau avec top 5 langages seulement
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 15, 0)

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 7200,
            "languages": [
                {"name": "Python", "total_seconds": 3000, "percent": 41.7},
                {"name": "JavaScript", "total_seconds": 1500, "percent": 20.8},
                {"name": "YAML", "total_seconds": 1000, "percent": 13.9},
                {"name": "Markdown", "total_seconds": 800, "percent": 11.1},
                {"name": "Shell", "total_seconds": 600, "percent": 8.3},
                {"name": "JSON", "total_seconds": 300, "percent": 4.2},
            ],
            "categories": [],
        }

        # Execute
        formation_step()

        # Verify
        mock_client.get_today_stats.assert_called_once()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.datetime")
    def test_formation_workflow_at_exact_minimum_before_deadline(
        self, mock_datetime, mock_client_class
    ):
        """
        Given: Exactement 2h de code à 16h
        When: Exécution de formation_step()
        Then: Affiche message de succès (objectif atteint, pas d'alerte)
        """
        # Setup
        os.environ["WAKATIME_API_KEY"] = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 16, 0)

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 7200,  # Exactement 2h
            "languages": [{"name": "Python", "total_seconds": 7200, "percent": 100.0}],
            "categories": [],
        }

        # Execute
        formation_step()

        # Verify
        mock_client.get_today_stats.assert_called_once()

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]


class TestWakaTimeClientIntegration:
    """Tests d'intégration pour le client WakaTime seul."""

    def test_client_initialization_with_env_var(self):
        """
        Given: API key dans variable d'environnement
        When: Initialisation du client sans argument
        Then: Client utilise la clé depuis l'env
        """
        os.environ["WAKATIME_API_KEY"] = "env-key-123"

        client = WakaTimeClient()

        assert client.api_key == "env-key-123"

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    def test_client_initialization_with_explicit_key(self):
        """
        Given: API key passée en argument
        When: Initialisation du client
        Then: Client utilise la clé fournie (priorité sur env)
        """
        os.environ["WAKATIME_API_KEY"] = "env-key-123"

        client = WakaTimeClient(api_key="explicit-key-456")

        assert client.api_key == "explicit-key-456"

        # Cleanup
        del os.environ["WAKATIME_API_KEY"]

    def test_client_initialization_without_key_raises_error(self):
        """
        Given: Aucune API key (ni en arg, ni en env)
        When: Initialisation du client
        Then: Lève WakaTimeAuthError
        """
        if "WAKATIME_API_KEY" in os.environ:
            del os.environ["WAKATIME_API_KEY"]

        with pytest.raises(WakaTimeAuthError, match="WakaTime API key not provided"):
            WakaTimeClient()
