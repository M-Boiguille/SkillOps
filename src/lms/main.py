"""Main entry point for SkillOps LMS CLI application."""

from pathlib import Path
from typing import Optional

import typer
from src.lms.cli import main_menu, execute_step
from src.lms.steps.notify import notify_step
from src.lms.steps.share import share_step

app = typer.Typer(
    name="skillops",
    help="SkillOps - Your Daily Learning Management System",
    add_completion=False,
)


@app.command()
def start():
    """Start the interactive SkillOps LMS menu."""
    while True:
        step = main_menu()
        if step is None:
            break
        execute_step(step)


@app.command()
def version():
    """Display the SkillOps version."""
    typer.echo("SkillOps LMS v0.1.0 (Sprint 1 MVP)")


@app.command()
def notify(
    storage_path: Optional[Path] = typer.Option(
        None, "--storage-path", help="Custom storage directory"
    ),
    respect_schedule: bool = typer.Option(
        False, "--respect-schedule", help="Send only at TELEGRAM_SCHEDULE_TIME"
    ),
):
    """Send today's notification to Telegram."""
    notify_step(storage_path=storage_path, respect_schedule=respect_schedule)


@app.command()
def share(
    labs_path: Optional[str] = typer.Option(
        None, "--labs-path", help="Path to labs directory"
    ),
    github_token: Optional[str] = typer.Option(
        None, "--github-token", help="GitHub personal access token"
    ),
    github_username: Optional[str] = typer.Option(
        None, "--github-username", help="GitHub username"
    ),
):
    """Share lab projects to GitHub with automatic README generation."""
    success = share_step(
        labs_path=labs_path,
        github_token=github_token,
        github_username=github_username,
    )
    if not success:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
