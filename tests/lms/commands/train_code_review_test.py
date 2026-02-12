from typer.testing import CliRunner

from src.lms.main import app


runner = CliRunner()


def test_train_command_offline(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    monkeypatch.setenv("SKILLOPS_TRAIN_OFFLINE", "1")

    result = runner.invoke(
        app,
        ["train", "docker", "--questions", "2"],
        input="ans1\nans2\n",
    )

    assert result.exit_code == 0
    assert "Session terminée" in result.stdout


def test_code_command(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))

    result = runner.invoke(app, ["code"])

    assert result.exit_code == 0
    assert "Mode code" in result.stdout


def test_review_command_no_session(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))

    result = runner.invoke(app, ["review"])

    assert result.exit_code == 0
    assert "Aucune session" in result.stdout
