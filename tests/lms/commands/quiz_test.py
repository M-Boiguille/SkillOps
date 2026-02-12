from typer.testing import CliRunner

from src.lms.main import app


runner = CliRunner()


def test_quiz_command_offline(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    monkeypatch.setenv("SKILLOPS_QUIZ_OFFLINE", "1")

    result = runner.invoke(
        app,
        ["quiz", "kubernetes", "--count", "2"],
        input="ans1\nans2\n",
    )

    assert result.exit_code == 0
    assert "Quiz terminé" in result.stdout
