"""Read step - review recent Obsidian notes and record progress."""

from __future__ import annotations

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table

from src.lms.database import get_connection, get_current_session_id, init_db
from src.lms.paths import get_storage_path

console = Console()


def get_vault_path() -> Optional[Path]:
    vault = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    if not vault:
        return None
    return Path(vault).expanduser().absolute()


def list_recent_notes(vault_path: Path, limit: int = 5) -> List[Path]:
    files = list(vault_path.rglob("*.md"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def save_read_progress(storage_path: Path, notes: List[Path]) -> None:
    init_db(storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    session_id = get_current_session_id(storage_path)
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO read_sessions (session_id, notes) VALUES (?, ?)",
        (session_id, json.dumps([str(n) for n in notes])),
    )
    conn.commit()
    conn.close()


def read_step(
    vault_path: Optional[Path] = None, storage_path: Optional[Path] = None
) -> bool:
    """Review recent notes from Obsidian and record the session."""
    vault = vault_path or get_vault_path()
    if not vault:
        console.print("[red]OBSIDIAN_VAULT_PATH not configured.[/red]")
        return False
    if not vault.exists() or not vault.is_dir():
        console.print(f"[red]Vault path is invalid: {vault}[/red]")
        return False

    recent = list_recent_notes(vault)
    if not recent:
        console.print("[yellow]No markdown notes found in the vault.[/yellow]")
        return False

    table = Table(title="Recent Notes")
    table.add_column("Note", style="cyan")
    table.add_column("Modified", style="magenta")

    for note in recent:
        mtime = datetime.fromtimestamp(note.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        table.add_row(note.name, mtime)

    console.print(table)

    save_read_progress(storage_path or get_storage_path(), recent)
    console.print("[green]Read session recorded.[/green]")
    return True
