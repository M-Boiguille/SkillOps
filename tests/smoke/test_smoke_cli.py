from typer.testing import CliRunner

from src.lms.main import app


runner = CliRunner()


def test_cli_help_smoke():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_cli_version_smoke():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "SkillOps" in result.stdout
