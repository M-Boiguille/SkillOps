"""Health check command for SkillOps."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console

console = Console()


def check_api_token(name: str, env_var: str) -> bool:
    """Check if an API token is set and non-empty with format hints."""
    token = os.getenv(env_var, "").strip()
    if not token:
        console.print(f"  [yellow]⚠ {name}: not configured[/yellow]")
        return False

    if env_var == "WAKATIME_API_KEY":
        pattern = re.compile(
            r"^waka_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        if not pattern.match(token):
            console.print(
                "  [yellow]⚠ WakaTime: token format looks invalid "
                "(expected waka_xxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)[/yellow]"
            )
            return False

    console.print(f"  [green]✓ {name}: configured[/green]")
    return True


def is_fine_grained_github_token(token: str) -> bool:
    """Best-effort detection of fine-grained PATs (github_pat_ prefix)."""
    return token.startswith("github_pat_")


def check_github_token() -> bool:
    """Verify GitHub token validity and surface scope hints."""
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        console.print("  [yellow]⚠ GitHub: token not set[/yellow]")
        return False

    headers = {"Authorization": f"token {token}"}
    try:
        response = requests.get(
            "https://api.github.com/user", headers=headers, timeout=5
        )
        if response.status_code == 200:
            username = response.json().get("login", "Unknown")
            scopes_header = response.headers.get("X-OAuth-Scopes", "") or ""
            scopes = [s.strip() for s in scopes_header.split(",") if s.strip()]
            fine_grained = is_fine_grained_github_token(token)

            console.print(f"  [green]✓ GitHub: authenticated as {username}[/green]")
            if fine_grained:
                console.print(
                    "  [dim]GitHub: fine-grained PAT detected (preferred)[/dim]"
                )
            else:
                if scopes:
                    console.print(f"  [dim]GitHub scopes: {', '.join(scopes)}[/dim]")
                    if "repo" not in scopes:
                        console.print(
                            "  [yellow]⚠ GitHub: classic token without 'repo' "
                            "scope may fail 'share' step[/yellow]"
                        )
                else:
                    console.print(
                        "  [yellow]⚠ GitHub: scopes not reported; ensure 'repo' "
                        "scope for classic tokens[/yellow]"
                    )
            return True

        console.print(
            f"  [red]✗ GitHub: token invalid (HTTP {response.status_code})[/red]"
        )
        return False
    except requests.RequestException as e:
        console.print(f"  [yellow]⚠ GitHub: network error ({str(e)[:30]}...)[/yellow]")
        return False


def check_telegram_token() -> bool:
    """Verify Telegram bot token is valid."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        console.print("  [yellow]⚠ Telegram: token not set[/yellow]")
        return False

    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
        if response.status_code == 200 and response.json().get("ok"):
            bot_name = response.json().get("result", {}).get("first_name", "Unknown")
            console.print(f"  [green]✓ Telegram: bot '{bot_name}' active[/green]")
            return True
        else:
            console.print("[red]✗ Telegram: token invalid[/red]")
            return False
    except requests.RequestException as e:
        console.print(
            f"  [yellow]⚠ Telegram: network error ({str(e)[:30]}...)[/yellow]"
        )
        return False


def check_directory(name: str, env_var: str, default: Optional[Path] = None) -> bool:
    """Check if a directory exists and is accessible."""
    path_str = os.getenv(env_var, "").strip()

    if not path_str and default:
        path_str = str(default)

    if not path_str:
        console.print(f"  [yellow]⚠ {name}: not configured[/yellow]")
        return False

    path = Path(path_str).expanduser().absolute()

    if path.exists() and path.is_dir():
        console.print(f"  [green]✓ {name}: {path}[/green]")
        return True
    else:
        console.print(f"  [yellow]⚠ {name}: directory not found ({path})[/yellow]")
        return False


def health_check() -> bool:
    """Perform health check of SkillOps configuration and connectivity.

    Returns:
        True if all critical components are healthy, False otherwise.
    """
    console.print("\n[bold cyan]SkillOps Health Check[/bold cyan]\n")

    all_healthy = True

    # Check API Tokens
    console.print("[bold cyan]API Credentials:[/bold cyan]")
    all_healthy &= check_api_token("WakaTime", "WAKATIME_API_KEY")
    all_healthy &= check_api_token("Gemini", "GEMINI_API_KEY")
    all_healthy &= check_api_token("GitHub Token", "GITHUB_TOKEN")
    all_healthy &= check_github_token()
    all_healthy &= check_api_token("Telegram Token", "TELEGRAM_BOT_TOKEN")
    all_healthy &= check_telegram_token()

    # Check Directories
    console.print("\n[bold cyan]Directories:[/bold cyan]")
    all_healthy &= check_directory(
        "Storage", "STORAGE_PATH", Path.home() / ".local/share/skillops"
    )
    all_healthy &= check_directory("Labs", "LABS_PATH", Path.home() / "labs")

    # Optional: Obsidian Vault
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    if vault_path:
        console.print("  [dim]Obsidian Vault: checking...[/dim]")
        if check_directory("Obsidian Vault", "OBSIDIAN_VAULT_PATH"):
            all_healthy &= True
        else:
            all_healthy = False
    else:
        console.print("  [dim]Obsidian Vault: not configured (optional)[/dim]")

    # Summary
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    if all_healthy:
        console.print("[green]✓ All critical components are healthy[/green]\n")
        return True
    else:
        console.print("[yellow]⚠ Some components need attention[/yellow]\n")
        return False
