"""Interactive setup wizard to generate a .env file and validate essentials."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import typer
from rich.console import Console

from src.lms.commands.health import health_check

console = Console()


ESSENTIAL_KEYS = [
    "WAKATIME_API_KEY",
    "GITHUB_TOKEN",
    "GITHUB_USERNAME",
]

OPTIONAL_KEYS = [
    "GEMINI_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "OBSIDIAN_VAULT_PATH",
    "LABS_PATH",
    "STORAGE_PATH",
]


def build_env_lines(config: Dict[str, str]) -> str:
    """Serialize config dict to env file content."""
    lines = []
    for key, value in config.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def run_setup_wizard(
    output_path: Path,
    non_interactive_inputs: Optional[Dict[str, str]] = None,
    run_health: bool = True,
) -> bool:
    """Create a .env file interactively or from provided inputs."""

    config: Dict[str, str] = {}

    def _ask(key: str, prompt_text: str, default: str = "") -> str:
        if non_interactive_inputs is not None and key in non_interactive_inputs:
            return non_interactive_inputs[key]
        return typer.prompt(prompt_text, default=default, hide_input="TOKEN" in key)

    # Essentials
    config["WAKATIME_API_KEY"] = _ask(
        "WAKATIME_API_KEY", "WakaTime API Key (waka_xxxx-xxxx-...)", ""
    )
    config["GITHUB_TOKEN"] = _ask(
        "GITHUB_TOKEN", "GitHub token (fine-grained preferred)", ""
    )
    config["GITHUB_USERNAME"] = _ask("GITHUB_USERNAME", "GitHub username", "")

    # Optional
    config["GEMINI_API_KEY"] = _ask("GEMINI_API_KEY", "Gemini API Key", "")
    config["TELEGRAM_BOT_TOKEN"] = _ask("TELEGRAM_BOT_TOKEN", "Telegram bot token", "")
    config["TELEGRAM_CHAT_ID"] = _ask("TELEGRAM_CHAT_ID", "Telegram chat id", "")

    default_storage = str(Path.home() / ".local/share/skillops")
    config["STORAGE_PATH"] = _ask("STORAGE_PATH", "Storage path", default_storage)

    default_labs = str(Path.home() / "labs")
    config["LABS_PATH"] = _ask("LABS_PATH", "Labs path", default_labs)

    config["OBSIDIAN_VAULT_PATH"] = _ask(
        "OBSIDIAN_VAULT_PATH", "Obsidian vault path (optional)", ""
    )

    # Write file
    output_path = output_path.expanduser().absolute()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_env_lines(config), encoding="utf-8")
    console.print(f"[green]✓ Wrote configuration to {output_path}[/green]")

    # Run health check to validate
    if run_health:
        console.print("\n[bold cyan]Running health check...[/bold cyan]")
        health_check()

    return True


def setup_command(output: Path = Path(".env"), skip_health: bool = False) -> None:
    """Typer entrypoint for the setup wizard command."""
    # If file exists, ask before overwriting
    if output.exists():
        overwrite = typer.confirm(
            f"{output} exists. Overwrite?", default=False, abort=False
        )
        if not overwrite:
            console.print("[yellow]Aborted: existing file preserved.[/yellow]")
            return

    run_setup_wizard(output, non_interactive_inputs=None, run_health=not skip_health)
