"""Doctor module - System health check and diagnostics."""

import os
import importlib.util
import sqlite3
from pathlib import Path
from rich.console import Console
from rich.table import Table
from src.lms.database import get_connection
from src.lms.paths import get_storage_path
from src.lms.secrets import _keyring_available

console = Console()


def check_env_var(var_name: str, required: bool = True) -> tuple[bool, str]:
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    if value:
        masked = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
        return True, f"[green]Set[/green] ({masked})"
    if required:
        return False, "[red]Missing[/red]"
    return True, "[yellow]Not Set (Optional)[/yellow]"


def check_module(module_name: str) -> tuple[bool, str]:
    """Check if a python module is installed."""
    if importlib.util.find_spec(module_name):
        return True, "[green]Installed[/green]"
    return False, "[red]Not Installed[/red]"


def check_log_format() -> tuple[bool, str]:
    """Validate SKILLOPS_LOG_FORMAT value."""
    value = os.getenv("SKILLOPS_LOG_FORMAT", "text").lower()
    if value in {"text", "json"}:
        return True, f"[green]{value}[/green]"
    return False, f"[red]Invalid[/red] ({value})"


def check_day_start_hour() -> tuple[bool, str]:
    """Validate SKILLOPS_DAY_START_HOUR value."""
    value = os.getenv("SKILLOPS_DAY_START_HOUR", "4")
    try:
        hour = int(value)
    except ValueError:
        return False, f"[red]Invalid[/red] ({value})"
    if 0 <= hour <= 23:
        return True, f"[green]{hour}[/green]"
    return False, f"[red]Out of range[/red] ({hour})"


def check_database() -> tuple[bool, str]:
    """Check database connection."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        return True, f"[green]Connected[/green] (SQLite {version})"
    except sqlite3.Error as e:
        return False, f"[red]Error:[/red] {e}"


def check_database_integrity() -> tuple[bool, str]:
    """Run SQLite integrity check."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        if result.lower() == "ok":
            return True, "[green]OK[/green]"
        return False, f"[red]{result}[/red]"
    except sqlite3.Error as e:
        return False, f"[red]Error:[/red] {e}"


def check_database_consistency() -> tuple[bool, str]:
    """Check basic relational consistency between incidents and postmortems."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM incidents
            WHERE postmortem_id IS NOT NULL
              AND postmortem_id NOT IN (SELECT id FROM postmortems)
            """
        )
        missing_postmortems = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM postmortems
            WHERE incident_id NOT IN (SELECT id FROM incidents)
            """
        )
        orphan_postmortems = cursor.fetchone()[0]

        conn.close()

        if missing_postmortems == 0 and orphan_postmortems == 0:
            return True, "[green]OK[/green]"
        details = (
            "missing_postmortems="
            f"{missing_postmortems}, orphan_postmortems={orphan_postmortems}"
        )
        return False, f"[red]{details}[/red]"
    except sqlite3.Error as e:
        return False, f"[red]Error:[/red] {e}"


def check_storage() -> tuple[bool, str]:
    """Check storage directory permissions."""
    path = get_storage_path()
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True, f"[green]Writable[/green] ({path})"
    except OSError as e:
        return False, f"[red]Error:[/red] {e}"


def check_keyring() -> tuple[bool, str]:
    """Check if keyring backend is available."""
    if _keyring_available():
        return True, "[green]Available[/green]"
    return False, "[yellow]Not available[/yellow]"


def check_config_permissions() -> tuple[bool, str]:
    """Check permissions for user config env file."""
    config_env = Path.home() / ".config" / "skillops" / "skillops.env"
    if not config_env.exists():
        return True, "[yellow]Not found[/yellow]"
    mode = config_env.stat().st_mode & 0o777
    if mode <= 0o600:
        return True, f"[green]{oct(mode)}[/green]"
    return False, f"[red]{oct(mode)}[/red] (should be 0o600)"


def run_doctor() -> bool:
    """Run all health checks."""
    table = Table(title="🚑 SkillOps Doctor", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")

    # 1. Environment Variables
    checks = [
        ("ENV: WAKATIME_API_KEY", *check_env_var("WAKATIME_API_KEY", required=False)),
        ("ENV: GEMINI_API_KEY", *check_env_var("GEMINI_API_KEY", required=False)),
        ("ENV: GITHUB_TOKEN", *check_env_var("GITHUB_TOKEN", required=False)),
        (
            "ENV: TELEGRAM_BOT_TOKEN",
            *check_env_var("TELEGRAM_BOT_TOKEN", required=False),
        ),
        (
            "ENV: OBSIDIAN_VAULT_PATH",
            *check_env_var("OBSIDIAN_VAULT_PATH", required=False),
        ),
        ("ENV: ANKI_SYNC_PATH", *check_env_var("ANKI_SYNC_PATH", required=False)),
        ("ENV: LABS_PATH", *check_env_var("LABS_PATH", required=False)),
    ]

    # 2. Dependencies
    checks.append(("DEP: google.genai", *check_module("google.genai")))
    checks.append(("DEP: keyring", *check_keyring()))
    checks.append(("DEP: typer", *check_module("typer")))
    checks.append(("DEP: rich", *check_module("rich")))
    checks.append(("DEP: inquirer", *check_module("inquirer")))
    checks.append(("DEP: readchar", *check_module("readchar")))
    checks.append(("CFG: SKILLOPS_LOG_FORMAT", *check_log_format()))
    checks.append(("CFG: SKILLOPS_DAY_START_HOUR", *check_day_start_hour()))

    # 3. System
    checks.append(("SYS: Storage", *check_storage()))
    checks.append(("SYS: Database", *check_database()))
    checks.append(("SYS: Database Integrity", *check_database_integrity()))
    checks.append(("SYS: Database Consistency", *check_database_consistency()))
    checks.append(("SYS: Config Env Perms", *check_config_permissions()))

    all_ok = True
    for name, success, details in checks:
        status = "✅ OK" if success else "❌ FAIL"
        if not success:
            all_ok = False
        table.add_row(name, status, details)

    console.print(table)
    return all_ok
