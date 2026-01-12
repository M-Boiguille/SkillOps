"""Tests for the interactive setup wizard (non-interactive path)."""

from src.lms.commands.setup_wizard import build_env_lines, run_setup_wizard


def test_build_env_lines_serializes_in_order():
    content = build_env_lines({"A": "1", "B": "2"})
    assert "A=1" in content.splitlines()[0]
    assert "B=2" in content.splitlines()[1]


def test_run_setup_wizard_writes_env_and_runs_health(monkeypatch, tmp_path):
    # Provide non-interactive inputs and stub health_check to avoid network
    inputs = {
        "WAKATIME_API_KEY": "waka_00000000-0000-0000-0000-000000000000",
        "GITHUB_TOKEN": "github_pat_test",
        "GITHUB_USERNAME": "tester",
        "GEMINI_API_KEY": "",
        "TELEGRAM_BOT_TOKEN": "",
        "TELEGRAM_CHAT_ID": "",
        "STORAGE_PATH": str(tmp_path / "storage"),
        "LABS_PATH": str(tmp_path / "labs"),
        "OBSIDIAN_VAULT_PATH": "",
    }

    called = {"health": False}

    def fake_health():
        called["health"] = True
        return True

    monkeypatch.setattr("src.lms.commands.setup_wizard.health_check", fake_health)

    output = tmp_path / "out.env"
    ok = run_setup_wizard(output, non_interactive_inputs=inputs, run_health=True)
    assert ok is True
    data = output.read_text()
    assert "WAKATIME_API_KEY=waka_00000000" in data
    assert called["health"] is True


def test_run_setup_wizard_respects_skip_health(monkeypatch, tmp_path):
    inputs = {
        "WAKATIME_API_KEY": "waka_00000000-0000-0000-0000-000000000000",
        "GITHUB_TOKEN": "github_pat_test",
        "GITHUB_USERNAME": "tester",
        "GEMINI_API_KEY": "",
        "TELEGRAM_BOT_TOKEN": "",
        "TELEGRAM_CHAT_ID": "",
        "STORAGE_PATH": str(tmp_path / "storage"),
        "LABS_PATH": str(tmp_path / "labs"),
        "OBSIDIAN_VAULT_PATH": "",
    }

    called = {"health": False}

    def fake_health():
        called["health"] = True
        return True

    monkeypatch.setattr("src.lms.commands.setup_wizard.health_check", fake_health)

    output = tmp_path / "out.env"
    ok = run_setup_wizard(output, non_interactive_inputs=inputs, run_health=False)
    assert ok is True
    assert called["health"] is False
