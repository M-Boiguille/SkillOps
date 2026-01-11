"""Main entry point for SkillOps LMS CLI application."""

import os
import time
from pathlib import Path
from typing import Optional

import typer
from src.lms.cli import main_menu, execute_step
from src.lms.commands.health import health_check
from src.lms.monitoring import (
    ErrorAggregator,
    MetricsCollector,
    send_alert_from_aggregator,
)
from src.lms.steps.notify import notify_step
from src.lms.steps.share import share_step

app = typer.Typer(
    name="skillops",
    help="SkillOps - Your Daily Learning Management System",
    add_completion=False,
)


def _alert_type() -> str:
    """Resolve alert type from environment (email/webhook/both)."""
    return os.getenv("SKILLOPS_ALERT_TYPE", "email")


@app.command()
def start(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose debug logging output",
    ),
    enable_monitoring: bool = typer.Option(
        False,
        "--enable-monitoring",
        help="Record metrics and send alerts on failures",
    ),
):
    """Start the interactive SkillOps LMS menu."""
    if verbose:
        from src.lms.logging_config import setup_logging

        setup_logging(verbose=True)

    from src.lms.logging_config import get_logger

    logger = get_logger(__name__)
    aggregator = ErrorAggregator() if enable_monitoring else None
    metrics = MetricsCollector() if enable_monitoring else None
    alert_type = _alert_type() if enable_monitoring else "email"
    logger.debug("Starting SkillOps interactive menu")

    while True:
        step = main_menu()
        if step is None:
            logger.debug("User exited interactive menu")
            break
        step_started = time.monotonic()
        success = True
        try:
            execute_step(step)
        except Exception as exc:  # pragma: no cover - passthrough to Typer
            success = False
            if aggregator:
                is_new = aggregator.record_error(exc, f"step_{step.number}")
                if is_new:
                    send_alert_from_aggregator(aggregator, alert_type)
            raise
        finally:
            if metrics:
                metrics.record_step_execution(
                    f"step_{step.number}",
                    time.monotonic() - step_started,
                    success,
                    metadata={"step_name": step.name},
                )
    logger.debug("SkillOps menu session completed")


@app.command()
def version():
    """Display the SkillOps version."""
    typer.echo("SkillOps LMS v0.4.0 (Observability)")


@app.command()
def health():
    """Check SkillOps configuration and connectivity."""
    health_check()


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
    enable_monitoring: bool = typer.Option(
        False,
        "--enable-monitoring",
        help="Record metrics and send alerts on failures",
    ),
):
    """Send today's notification to Telegram."""
    if verbose:
        from src.lms.logging_config import setup_logging

        setup_logging(verbose=True)

    from src.lms.logging_config import get_logger

    logger = get_logger(__name__)
    aggregator = ErrorAggregator() if enable_monitoring else None
    metrics = MetricsCollector() if enable_monitoring else None
    alert_type = _alert_type() if enable_monitoring else "email"
    started_at = time.monotonic()
    success = False
    logger.debug(
        "Starting notify_step with storage_path=%s, respect_schedule=%s",
        storage_path,
        respect_schedule,
    )
    try:
        success = notify_step(
            storage_path=storage_path, respect_schedule=respect_schedule
        )
        if success:
            logger.debug("notify_step completed successfully")
        else:
            logger.warning("notify_step completed without sending notification")
    except Exception as exc:  # pragma: no cover - passthrough to Typer
        if aggregator:
            is_new = aggregator.record_error(exc, "notify")
            if is_new:
                send_alert_from_aggregator(aggregator, alert_type)
        raise
    finally:
        if metrics:
            metrics.record_step_execution(
                "notify",
                time.monotonic() - started_at,
                success,
                metadata={"respect_schedule": respect_schedule},
            )
    return success


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
    enable_monitoring: bool = typer.Option(
        False,
        "--enable-monitoring",
        help="Record metrics and send alerts on failures",
    ),
):
    """Share lab projects to GitHub with automatic README generation."""
    if verbose:
        from src.lms.logging_config import setup_logging

        setup_logging(verbose=True)

    from src.lms.logging_config import get_logger

    logger = get_logger(__name__)
    aggregator = ErrorAggregator() if enable_monitoring else None
    metrics = MetricsCollector() if enable_monitoring else None
    alert_type = _alert_type() if enable_monitoring else "email"
    started_at = time.monotonic()
    success = False
    logger.debug(
        "Starting share_step with labs_path=%s, github_username=%s",
        labs_path,
        github_username,
    )
    try:
        success = share_step(
            labs_path=labs_path,
            github_token=github_token,
            github_username=github_username,
        )
        if success:
            logger.debug("share_step completed successfully")
        else:
            logger.error("share_step failed")
            if aggregator:
                is_new = aggregator.record_error(
                    RuntimeError("share_step returned False"),
                    "share",
                    context={
                        "labs_path": labs_path,
                        "github_username": github_username,
                    },
                )
                if is_new:
                    send_alert_from_aggregator(aggregator, alert_type)
    except Exception as exc:  # pragma: no cover - passthrough to Typer
        logger.error("share_step raised exception: %s", exc)
        if aggregator:
            is_new = aggregator.record_error(
                exc,
                "share",
                context={
                    "labs_path": labs_path,
                    "github_username": github_username,
                },
            )
            if is_new:
                send_alert_from_aggregator(aggregator, alert_type)
        raise
    finally:
        if metrics:
            metrics.record_step_execution(
                "share",
                time.monotonic() - started_at,
                success,
                metadata={
                    "labs_path": labs_path,
                    "github_username": github_username,
                },
            )

    if not success:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
