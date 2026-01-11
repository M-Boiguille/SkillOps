"""Tests for the Anki step using AnkiConnect."""

from unittest.mock import patch

from src.lms.steps.anki import (
    get_anki_url_from_env,
    get_deck_names,
    get_due_counts_by_deck,
    anki_step,
)


class TestEnvUrl:
    def test_default_url(self, monkeypatch):
        monkeypatch.delenv("ANKI_CONNECT_URL", raising=False)
        assert get_anki_url_from_env() == "http://localhost:8765"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("ANKI_CONNECT_URL", "http://localhost:9999")
        assert get_anki_url_from_env() == "http://localhost:9999"


class TestDecksAndDueCounts:
    def test_get_deck_names_calls_anki(self):
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"result": ["Default", "Linux"]}
            names = get_deck_names()
            assert names == ["Default", "Linux"]
            assert mock_post.called

    def test_get_due_counts_by_deck_aggregates(self):
        calls = []

        def fake_post(url, json=None, timeout=5):
            calls.append(json["action"])

            class R:
                status_code = 200

                def json(self_inner):
                    action = json["action"]
                    if action == "deckNames":
                        return {"result": ["Default", "Linux"]}
                    if action == "findCards":
                        q = json["params"]["query"]
                        if "Default" in q:
                            return {"result": [1, 2, 3]}
                        return {"result": [42]}
                    return {"result": None}

            return R()

        with patch("requests.post", side_effect=fake_post):
            counts = get_due_counts_by_deck()
            assert counts == {"Default": 3, "Linux": 1}
            assert calls.count("deckNames") == 1
            assert calls.count("findCards") == 2


class TestAnkiStep:
    def test_anki_step_sync_when_env_true(self, monkeypatch):
        monkeypatch.setenv("ANKI_AUTO_SYNC", "true")

        def fake_post(url, json=None, timeout=5):
            class R:
                status_code = 200

                def json(self_inner):
                    action = json["action"]
                    if action == "deckNames":
                        return {"result": ["Default"]}
                    if action == "findCards":
                        return {"result": [1]}
                    if action == "sync":
                        return {"result": "OK", "error": None}
                    return {"result": None}

            return R()

        with patch("requests.post", side_effect=fake_post) as mock_post:
            anki_step()
            actions = [c.kwargs["json"]["action"] for c in mock_post.call_args_list]
            assert "sync" in actions
