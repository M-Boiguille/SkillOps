"""Main entry point for SkillOps LMS CLI application."""

# CRITICAL: Load environment variables FIRST, before any imports
from dotenv import load_dotenv

load_dotenv()

import os  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Optional  # noqa: E402

import typer  # noqa: E402

from src.lms.cli import main_menu, execute_step  # noqa: E402
from src.lms.commands.health import health_check  # noqa: E402
from src.lms.commands.export import DataExporter  # noqa: E402
from src.lms.commands.data_import import DataImporter  # noqa: E402
from src.lms.monitoring import (  # noqa: E402
    ErrorAggregator,
    MetricsCollector,
    send_alert_from_aggregator,
)
from src.lms.steps.notify import notify_step  # noqa: E402
from src.lms.steps.pagerduty import pagerduty_check  # noqa: E402
from src.lms.steps.missions import missions_step  # noqa: E402
from src.lms.steps.share import share_step  # noqa: E402
from src.lms.commands.setup_wizard import setup_command  # noqa: E402
from src.lms.books import (  # noqa: E402
    check_books_command,
    submit_books_command,
    fetch_books_command,
    import_books_command,
    process_pipeline_command,
)

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
    """Start the interactive SkillOps LMS menu.

    Launch the daily learning workflow with 9 steps:
    1. 📊 Daily Stand-up - Check yesterday's metrics & progress
    2. ⏱️ Metrics - Complete training modules (WakaTime)
    3. 🗂️ Flashcards - Review flashcards
    4. 📝 Create - Build projects or write code
    5. 📖 Read - Learn from technical articles
    6. 💪 Mission Control - Solve tickets & incidents
    7. 🌐 Pull Request - Publish learnings or insights
    8. 🌅 Reflection - Journal your progress
    9. 🎯 Labs - AI-powered learning missions

    Navigation:
        • Use ↑↓ or j/k to navigate
        • Press Enter to select
        • Press Ctrl+C to quit
    """
    if verbose:
        from src.lms.logging_config import setup_logging

        setup_logging(verbose=True)

    from src.lms.logging_config import get_logger

    logger = get_logger(__name__)
    aggregator = ErrorAggregator() if enable_monitoring else None
    metrics = MetricsCollector() if enable_monitoring else None
    alert_type = _alert_type() if enable_monitoring else "email"
    logger.debug("Starting SkillOps interactive menu")

    continue_to_menu = pagerduty_check(on_incident=missions_step)
    if not continue_to_menu:
        logger.debug("PagerDuty check halted the session")
        return

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
    """Display the SkillOps version and build info."""
    typer.echo("SkillOps LMS v0.5.0 (Labs & Polish)")


@app.command()
def health():
    """Check SkillOps configuration and all integrations.

    Validates:
        • Configuration files (.env, config.yaml)
        • API connections (Gemini AI, WakaTime, GitHub, Telegram)
        • Storage access
        • Required dependencies
    """
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


@app.command()
def setup(
    output: Path = typer.Option(
        Path(".env"),
        "--output",
        "-o",
        help="Path to write the generated .env file",
    ),
    skip_health: bool = typer.Option(
        False,
        "--skip-health",
        help="Skip running health check after writing .env",
    ),
):
    """Guided setup to create a .env file and validate configuration."""

    setup_command(output=output, skip_health=skip_health)


@app.command()
def export(
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Export format: json or csv",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file or directory path",
    ),
):
    """Export progress and metrics data for backup or analysis.

    Create portable backups of your learning progress in JSON or CSV format.
    Perfect for:
        • Backing up your learning history
        • Analyzing progress in Excel/BI tools
        • Migrating to new machine
        • Sharing statistics with your team

    JSON Format: Single file with complete progress history + metadata
    CSV Format: Flat table with date, steps, time, cards per row

    Examples:
        skillops export --format json --output backup.json
        skillops export --format csv --output ./exports/
        skillops export -f json -o ~/backups/$(date +%Y%m%d).json
    """
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    try:
        exporter = DataExporter()

        if format.lower() == "json":
            result = exporter.export_to_json(output_path=output)
            console.print(f"\n[green]✓ Exported to {result}[/green]\n")
        elif format.lower() == "csv":
            results = exporter.export_to_csv(output_dir=output)
            console.print(f"\n[green]✓ Exported {len(results)} " "CSV files[/green]\n")
        else:
            console.print("[red]✗ Invalid format. Use 'json' or 'csv'[/red]\n")
            raise typer.Exit(code=1)

        exporter.display_export_summary()

    except FileNotFoundError as exc:
        error_panel = Panel(
            f"[red]Directory not found:[/red] {exc}\n\n"
            "[yellow]Suggestion:[/yellow] Ensure the output directory "
            "exists or create it first:\n"
            f"  mkdir -p {output if output else './skillops_exports'}",
            title="[red]❌ Export Failed[/red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(code=1)
    except PermissionError:
        error_panel = Panel(
            "[red]Permission denied:[/red] Cannot write to output "
            "location\n\n"
            "[yellow]Suggestion:[/yellow] Check write permissions or "
            "choose a different directory:\n"
            "  skillops export -f json -o ~/skillops_backup.json",
            title="[red]❌ Export Failed[/red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(code=1)
    except Exception as exc:
        error_panel = Panel(
            f"[red]Export failed:[/red] {str(exc)}\n\n"
            f"[yellow]Tips:[/yellow]\n"
            f"  • Use --verbose flag for detailed error logs\n"
            f"  • Ensure all API keys are configured\n"
            f"  • Check available disk space",
            title="[red]❌ Export Error[/red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(code=1)


@app.command()
def import_data(
    file: Path = typer.Argument(
        ...,
        help="File or directory to import from",
    ),
    format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Import format: json or csv (auto-detected if omitted)",
    ),
    merge: bool = typer.Option(
        False,
        "--merge",
        "-m",
        help="Merge with existing data instead of replacing",
    ),
):
    """Import progress and metrics data.

    Restore your learning progress from a previous export.
    Creates a backup before importing (unless --no-backup).

    Examples:
        skillops import-data progress.json
        skillops import-data ./exports/ --format csv
        skillops import-data progress.json --merge
    """
    from rich.console import Console
    from rich.prompt import Confirm
    from rich.panel import Panel

    console = Console()

    if not file.exists():
        error_panel = Panel(
            f"[red]File not found:[/red] {file}\n\n"
            f"[yellow]Suggestions:[/yellow]\n"
            f"  • Double-check the file path\n"
            f"  • Try: skillops export -f json -o backup.json\n"
            f"  • Use absolute path: /home/user/backups/progress.json",
            title="[red]❌ Import Failed[/red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(code=1)

    try:
        importer = DataImporter()

        # Auto-detect format if not specified
        if format is None:
            if file.is_file() and file.suffix == ".json":
                format = "json"
            elif file.is_file() and file.suffix == ".csv":
                format = "csv"
            elif file.is_dir():
                format = "csv"
            else:
                error_panel = Panel(
                    f"[red]Could not auto-detect format[/red]\n\n"
                    f"[yellow]Please specify format:[/yellow]\n"
                    f"  skillops import-data {file} --format json\n"
                    f"  skillops import-data {file} --format csv",
                    title="[red]❌ Format Detection Failed[/red]",
                    border_style="red",
                )
                console.print(error_panel)
                raise typer.Exit(code=1)

        # Validate before importing
        if not importer.validate_import(file):
            error_panel = Panel(
                f"[red]Invalid import file:[/red] {file}\n\n"
                f"[yellow]Check:[/yellow]\n"
                f"  • JSON files must be valid JSON\n"
                f"  • CSV files must have: date, steps, time, cards\n"
                f"  • File is not corrupted",
                title="[red]❌ Validation Failed[/red]",
                border_style="red",
            )
            console.print(error_panel)
            raise typer.Exit(code=1)

        # Show confirmation
        merge_note = " (merging)" if merge else " (replacing existing data)"
        console.print(f"\n[yellow]⚠️  Importing from {file}{merge_note}" "[/yellow]")
        console.print(
            "[dim]A backup of current data will be created before " "import[/dim]"
        )

        if not Confirm.ask("Continue with import?"):
            console.print("[yellow]Import cancelled[/yellow]\n")
            raise typer.Exit(code=0)

        # Perform import
        if format.lower() == "json":
            success = importer.import_from_json(file, merge=merge, backup=True)
        elif format.lower() == "csv":
            success = importer.import_from_csv(file, merge=merge, backup=True)
        else:
            console.print("[red]✗ Invalid format. Use 'json' or 'csv'[/red]\n")
            raise typer.Exit(code=1)

        if success:
            console.print("\n[green]✓ Import completed successfully[/green]\n")
        else:
            error_panel = Panel(
                "[red]Import failed[/red]\n\n"
                "[yellow]Try:[/yellow]\n"
                "  • Check file format is correct\n"
                "  • Use --verbose flag for details\n"
                "  • Restore from backup in "
                "~/.skillops/profiles/backups/",
                title="[red]❌ Import Error[/red]",
                border_style="red",
            )
            console.print(error_panel)
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except FileNotFoundError:
        error_panel = Panel(
            "[red]File access error: Unable to read file[/red]\n\n"
            "[yellow]Ensure:[/yellow]\n"
            "  • File has correct permissions\n"
            "  • Directory exists and is readable",
            title="[red]❌ File Access Failed[/red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(code=1)
    except Exception as exc:
        error_panel = Panel(
            f"[red]Import failed:[/red] {str(exc)}\n\n"
            "[yellow]Debug tips:[/yellow]\n"
            "  • Run: skillops health (check system status)\n"
            f"  • Run: skillops import-data {file} --verbose (logs)\n"
            "  • Check file is not corrupted",
            title="[red]❌ Unexpected Error[/red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(code=1)


@app.command(name="check-books")
def check_books():
    """Display book processing queue status (read-only).

    Shows all books in the processing pipeline:
        • Pending: Ready to be submitted
        • Processing: Batch job running
        • Ready: Results available for import
        • Imported: Already imported to vault
        • Failed: Error during processing

    Example:
        skillops check-books
    """
    check_books_command()


@app.command(name="submit-books")
def submit_books(
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Gemini API key (or set GEMINI_API_KEY env var)",
        envvar="GEMINI_API_KEY",
    )
):
    """
    Submit pending PDFs for batch processing.

    Scans books/pending/ directory for PDF files and submits them
    to Gemini Batch API for extraction of:
    • Zettelkasten notes (atomic concepts)
    • Flashcards (Bloom's taxonomy)
    • Pareto summary (20% → 80% value)

    Each book creates 3 parallel batch requests with ~24h turnaround.

    Requirements:
        • GEMINI_API_KEY environment variable or --api-key flag
        • PDF files in books/pending/ directory

    Example:
        skillops submit-books
        skillops submit-books --api-key "your-api-key"
    """
    submit_books_command(api_key)


@app.command(name="fetch-books")
def fetch_books(
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Gemini API key (or set GEMINI_API_KEY env var)",
        envvar="GEMINI_API_KEY",
    ),
    book_name: Optional[str] = typer.Option(
        None,
        "--book",
        "-b",
        help="Specific book name to fetch (default: all processing books)",
    ),
):
    """
    Fetch results from completed batch jobs.

    Checks the status of all books in "processing" state and downloads
    completed results. For each completed batch job:
    • Downloads output JSONL from Gemini Batch API
    • Parses 3 JSON outputs (zettelkasten, flashcards, pareto)
    • Saves results to books/completed/{book}/results/
    • Updates manifest status: processing → completed

    Books that are still processing will show estimated time remaining.

    Requirements:
        • GEMINI_API_KEY environment variable or --api-key flag
        • Books must be in "processing" status

    Example:
        skillops fetch-books
        skillops fetch-books --book networking-sysadmins
    """
    fetch_books_command(api_key, book_name)


@app.command(name="import-books")
def import_books(
    vault_path: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Obsidian vault path (default: .skillopsvault)",
        envvar="OBSIDIAN_VAULT_PATH",
    ),
    book_name: Optional[str] = typer.Option(
        None,
        "--book",
        "-b",
        help="Specific book name to import (default: all completed books)",
    ),
):
    """
    Import completed books to Obsidian vault.

    Creates a structured knowledge base from extracted JSON results:
    • Zettelkasten notes → Individual atomic concept files with backlinks
    • Flashcards → Single deck file with spaced repetition format
    • Pareto summaries → Must-know/should-know concepts + learning path
    • MOC (Map of Content) → Index file linking all content

    Vault structure:
        .skillopsvault/{book}/
        ├── 00-INDEX.md              # Map of Content
        ├── zettelkasten/
        │   ├── ch1_001.md
        │   └── ...
        ├── flashcards/
        │   └── {book}-deck.md
        └── pareto/
            ├── must-know.md
            ├── should-know.md
            └── learning-path.md

    Updates manifest status: completed → imported

    Requirements:
        • Books must be in "completed" status
        • Valid OBSIDIAN_VAULT_PATH or --vault flag

    Example:
        skillops import-books
        skillops import-books --vault ~/MyVault --book docker-deep-dive
    """
    import_books_command(vault_path, book_name)


@app.command(name="process-pipeline")
def process_pipeline(
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Gemini API key (or set GEMINI_API_KEY env var)",
        envvar="GEMINI_API_KEY",
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w", help="Enable watch mode for continuous polling"
    ),
    interval: int = typer.Option(
        30, "--interval", "-i", help="Polling interval in minutes (for --watch mode)"
    ),
):
    """
    Complete book processing pipeline (all-in-one).

    Runs the full workflow in a single command:
    1. Submit pending PDFs for batch processing
    2. Monitor until completion (optional --watch mode)
    3. Fetch results from Gemini Batch API
    4. Import to Obsidian vault

    Two modes:

    **One-time mode (default):**
    - Submits pending books
    - Fetches results (assumes already processing)
    - Imports completed books
    - Exits immediately

    **Watch mode (--watch):**
    - Submits pending books
    - Polls every N minutes (default 30min)
    - Auto-fetches when completed
    - Auto-imports when ready
    - Continues until all books are processed
    - Press Ctrl+C to stop watching

    Examples:
        # One-time run (good for cron/CI)
        skillops process-pipeline

        # Watch mode with default 30min interval
        skillops process-pipeline --watch

        # Custom polling interval
        skillops process-pipeline --watch --interval 15

    Requirements:
        • GEMINI_API_KEY environment variable or --api-key flag
        • PDFs in books/pending/ (for submit)
        • Valid OBSIDIAN_VAULT_PATH or .skillopsvault
    """
    process_pipeline_command(api_key, watch, interval)


def main():
    """Main entry point for console_scripts."""
    app()


if __name__ == "__main__":
    app()
