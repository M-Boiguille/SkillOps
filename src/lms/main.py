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
def start(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose debug logging output",
    ),
):
    """Start the interactive SkillOps LMS menu."""
    if verbose:
        from src.lms.logging_config import setup_logging

        setup_logging(verbose=True)

    from src.lms.logging_config import get_logger

    logger = get_logger(__name__)
    logger.debug("Starting SkillOps interactive menu")

    while True:
        step = main_menu()
        if step is None:
            logger.debug("User exited interactive menu")
            break
        execute_step(step)
    logger.debug("SkillOps menu session completed")


@app.command()
def version():
    """Display the SkillOps version."""
    typer.echo("SkillOps LMS v0.1.0 (Sprint 1 MVP)")


@app.command()
def notify(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose debug logging output",
    ),
    storage_path: Optional[Path] = typer.Option(
        None, "--storage-path", help="Custom storage directory"
    ),
    respect_schedule: bool = typer.Option(
        False, "--respect-schedule", help="Send only at TELEGRAM_SCHEDULE_TIME"
    ),
):
    """Send today's notification to Telegram."""
    if verbose:
        from src.lms.logging_config import setup_logging

        setup_logging(verbose=True)

    from src.lms.logging_config import get_logger

    logger = get_logger(__name__)
    logger.debug(
        "Starting notify_step with storage_path=%s, respect_schedule=%s",
        storage_path,
        respect_schedule,
    )
    notify_step(storage_path=storage_path, respect_schedule=respect_schedule)
    logger.debug("notify_step completed successfully")


@app.command()
def share(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose debug logging output",
    ),
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
    if verbose:
        from src.lms.logging_config import setup_logging

        setup_logging(verbose=True)

    from src.lms.logging_config import get_logger

    logger = get_logger(__name__)
    logger.debug(
        "Starting share_step with labs_path=%s, github_username=%s",
        labs_path,
        github_username,
    )
    success = share_step(
        labs_path=labs_path,
        github_token=github_token,
        github_username=github_username,
    )
    if success:
        logger.debug("share_step completed successfully")
    else:
        logger.error("share_step failed")

    if not success:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
