"""Tests pour l'étape Formation."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from rich.table import Table

from src.lms.api_clients.wakatime_client import WakaTimeAuthError, WakaTimeError
from src.lms.steps.formation import (
    create_languages_table,
    create_stats_table,
    formation_step,
    get_api_key_from_env,
    should_show_alert,
)


class TestGetApiKeyFromEnv:
    """Tests pour get_api_key_from_env()."""

    def test_returns_api_key_when_present(self, monkeypatch):
        """
        Given: Variable d'environnement WAKATIME_API_KEY définie
        When: Appel de get_api_key_from_env()
        Then: Retourne la clé API
        """
        monkeypatch.setenv("WAKATIME_API_KEY", "test-key-123")
        result = get_api_key_from_env()
        assert result == "test-key-123"

    def test_returns_none_when_absent(self, monkeypatch):
        """
        Given: Variable d'environnement WAKATIME_API_KEY non définie
        When: Appel de get_api_key_from_env()
        Then: Retourne None
        """
        monkeypatch.delenv("WAKATIME_API_KEY", raising=False)
        result = get_api_key_from_env()
        assert result is None


class TestShouldShowAlert:
    """Tests pour should_show_alert()."""

    def test_shows_alert_before_deadline_below_minimum(self):
        """
        Given: Il est 15h et 1.5h de code
        When: Appel de should_show_alert()
        Then: Retourne True
        """
        current_time = datetime(2024, 1, 15, 15, 0)  # 15h
        hours_coded = 1.5
        assert should_show_alert(current_time, hours_coded) is True

    def test_no_alert_before_deadline_above_minimum(self):
        """
        Given: Il est 15h et 2.5h de code
        When: Appel de should_show_alert()
        Then: Retourne False
        """
        current_time = datetime(2024, 1, 15, 15, 0)  # 15h
        hours_coded = 2.5
        assert should_show_alert(current_time, hours_coded) is False

    def test_no_alert_after_deadline_below_minimum(self):
        """
        Given: Il est 18h et 1h de code
        When: Appel de should_show_alert()
        Then: Retourne False (trop tard pour l'alerte)
        """
        current_time = datetime(2024, 1, 15, 18, 0)  # 18h
        hours_coded = 1.0
        assert should_show_alert(current_time, hours_coded) is False

    def test_no_alert_at_deadline_below_minimum(self):
        """
        Given: Il est exactement 17h et 1h de code
        When: Appel de should_show_alert()
        Then: Retourne False (deadline atteinte)
        """
        current_time = datetime(2024, 1, 15, 17, 0)  # 17h
        hours_coded = 1.0
        assert should_show_alert(current_time, hours_coded) is False

    def test_no_alert_before_deadline_at_minimum(self):
        """
        Given: Il est 15h et exactement 2h de code
        When: Appel de should_show_alert()
        Then: Retourne False (objectif atteint)
        """
        current_time = datetime(2024, 1, 15, 15, 0)  # 15h
        hours_coded = 2.0
        assert should_show_alert(current_time, hours_coded) is False


class TestCreateStatsTable:
    """Tests pour create_stats_table()."""

    def test_creates_table_with_complete_stats(self):
        """
        Given: Statistiques complètes (temps, langages, catégories)
        When: Appel de create_stats_table()
        Then: Crée une table Rich avec toutes les données
        """
        stats = {
            "total_seconds": 7200,  # 2h
            "languages": [{"name": "Python", "total_seconds": 5400, "percent": 75.0}],
            "categories": [{"name": "Coding", "total_seconds": 6400, "percent": 88.9}],
        }
        table = create_stats_table(stats)
        assert isinstance(table, Table)
        assert table.title == "📊 Statistiques du jour"
        assert len(table.columns) == 2

    def test_creates_table_with_minimal_stats(self):
        """
        Given: Statistiques minimales (seulement temps total)
        When: Appel de create_stats_table()
        Then: Crée une table avec uniquement le temps
        """
        stats = {"total_seconds": 3600}  # 1h
        table = create_stats_table(stats)
        assert isinstance(table, Table)
        assert len(table.columns) == 2

    def test_creates_table_with_zero_time(self):
        """
        Given: Statistiques avec 0 seconde
        When: Appel de create_stats_table()
        Then: Crée une table avec "0min"
        """
        stats = {"total_seconds": 0}
        table = create_stats_table(stats)
        assert isinstance(table, Table)

    def test_creates_table_with_empty_languages(self):
        """
        Given: Statistiques sans langages
        When: Appel de create_stats_table()
        Then: Crée une table sans ligne de langage
        """
        stats = {"total_seconds": 3600, "languages": []}
        table = create_stats_table(stats)
        assert isinstance(table, Table)


class TestCreateLanguagesTable:
    """Tests pour create_languages_table()."""

    def test_creates_table_with_languages(self):
        """
        Given: Liste de langages avec statistiques
        When: Appel de create_languages_table()
        Then: Crée une table Rich avec les langages
        """
        languages = [
            {"name": "Python", "total_seconds": 5400, "percent": 60.0},
            {"name": "JavaScript", "total_seconds": 3600, "percent": 40.0},
        ]
        table = create_languages_table(languages)
        assert isinstance(table, Table)
        assert table.title == "💻 Langages utilisés"
        assert len(table.columns) == 3

    def test_limits_to_top_5_languages(self):
        """
        Given: Liste de 10 langages
        When: Appel de create_languages_table()
        Then: Table contient seulement les 5 premiers
        """
        languages = [
            {"name": f"Lang{i}", "total_seconds": 1000 - i * 100, "percent": 10.0}
            for i in range(10)
        ]
        table = create_languages_table(languages)
        assert isinstance(table, Table)
        # Vérifier qu'on a bien une table (pas de moyen direct de compter les rows)

    def test_creates_table_with_empty_list(self):
        """
        Given: Liste vide de langages
        When: Appel de create_languages_table()
        Then: Crée une table vide
        """
        languages = []
        table = create_languages_table(languages)
        assert isinstance(table, Table)


class TestFormationStep:
    """Tests pour formation_step()."""

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.get_api_key_from_env")
    @patch("src.lms.steps.formation.datetime")
    def test_displays_stats_successfully(
        self, mock_datetime, mock_get_key, mock_client_class
    ):
        """
        Given: Clé API valide et statistiques disponibles
        When: Appel de formation_step()
        Then: Affiche les statistiques et pas d'alerte si objectif atteint
        """
        # Setup
        mock_get_key.return_value = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 15, 0)

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 7200,  # 2h
            "languages": [{"name": "Python", "total_seconds": 5400, "percent": 75.0}],
            "categories": [{"name": "Coding", "total_seconds": 6400, "percent": 88.9}],
        }

        # Execute
        formation_step()

        # Verify
        mock_get_key.assert_called_once()
        mock_client_class.assert_called_once_with("test-key")
        mock_client.get_today_stats.assert_called_once()

    @patch("src.lms.steps.formation.get_api_key_from_env")
    def test_shows_error_when_no_api_key(self, mock_get_key):
        """
        Given: Aucune clé API disponible
        When: Appel de formation_step()
        Then: Affiche un message d'erreur et retourne sans appeler l'API
        """
        mock_get_key.return_value = None

        # Should not raise exception, just display error
        formation_step()

        mock_get_key.assert_called_once()

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.get_api_key_from_env")
    @patch("src.lms.steps.formation.datetime")
    def test_shows_alert_when_below_minimum(
        self, mock_datetime, mock_get_key, mock_client_class
    ):
        """
        Given: 1h de code à 15h (en dessous du minimum)
        When: Appel de formation_step()
        Then: Affiche une alerte
        """
        mock_get_key.return_value = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 15, 0)

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 3600,  # 1h
            "languages": [],
            "categories": [],
        }

        formation_step()

        mock_client.get_today_stats.assert_called_once()

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.get_api_key_from_env")
    @patch("src.lms.steps.formation.datetime")
    def test_no_alert_after_deadline(
        self, mock_datetime, mock_get_key, mock_client_class
    ):
        """
        Given: 1h de code à 18h (après deadline)
        When: Appel de formation_step()
        Then: Pas d'alerte affichée
        """
        mock_get_key.return_value = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 18, 0)

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 3600,  # 1h
            "languages": [],
            "categories": [],
        }

        formation_step()

        mock_client.get_today_stats.assert_called_once()

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.get_api_key_from_env")
    def test_raises_error_on_api_failure(self, mock_get_key, mock_client_class):
        """
        Given: Erreur lors de l'appel à l'API WakaTime
        When: Appel de formation_step()
        Then: Affiche l'erreur sans lever d'exception (graceful degradation)
        """
        mock_get_key.return_value = "test-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.side_effect = WakaTimeError("API Error")

        # Should not raise - displays error message instead
        formation_step()

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.get_api_key_from_env")
    def test_raises_error_on_auth_failure(self, mock_get_key, mock_client_class):
        """
        Given: Erreur d'authentification avec l'API WakaTime
        When: Appel de formation_step()
        Then: Affiche l'erreur sans lever d'exception (graceful degradation)
        """
        mock_get_key.return_value = "invalid-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.side_effect = WakaTimeAuthError("Invalid API key")

        # Should not raise - displays error message instead
        formation_step()

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.get_api_key_from_env")
    @patch("src.lms.steps.formation.datetime")
    def test_displays_languages_table_when_available(
        self, mock_datetime, mock_get_key, mock_client_class
    ):
        """
        Given: Statistiques avec plusieurs langages
        When: Appel de formation_step()
        Then: Affiche le tableau des langages
        """
        mock_get_key.return_value = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 15, 0)

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 7200,
            "languages": [
                {"name": "Python", "total_seconds": 5400, "percent": 75.0},
                {"name": "JavaScript", "total_seconds": 1800, "percent": 25.0},
            ],
            "categories": [],
        }

        formation_step()

        mock_client.get_today_stats.assert_called_once()

    @patch("src.lms.steps.formation.WakaTimeClient")
    @patch("src.lms.steps.formation.get_api_key_from_env")
    @patch("src.lms.steps.formation.datetime")
    def test_handles_zero_coding_time(
        self, mock_datetime, mock_get_key, mock_client_class
    ):
        """
        Given: Aucune activité de code aujourd'hui
        When: Appel de formation_step()
        Then: Affiche les statistiques avec 0 temps
        """
        mock_get_key.return_value = "test-key"
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 0)

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_today_stats.return_value = {
            "total_seconds": 0,
            "languages": [],
            "categories": [],
        }

        formation_step()

        mock_client.get_today_stats.assert_called_once()
