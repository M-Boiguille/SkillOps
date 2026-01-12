"""Reflection step - create a daily journal entry template."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def get_storage_path() -> Path:
    storage = os.getenv("STORAGE_PATH", str(Path.home() / ".local/share/skillops"))
    return Path(storage).expanduser().absolute()


def reflection_step(
    storage_path: Optional[Path] = None, target_date: Optional[str] = None
) -> bool:
    """Create a templated reflection note for today (or provided date)."""
    storage = storage_path or get_storage_path()
    reflections_dir = storage / "reflections"
    reflections_dir.mkdir(parents=True, exist_ok=True)

    date_str = target_date or datetime.now().strftime("%Y-%m-%d")
    note_file = reflections_dir / f"{date_str}.md"

    if note_file.exists():
        console.print(f"[yellow]Reflection already exists for {date_str}[/yellow]")
        return True

    template = """# Reflection - {date}

## Mood

## Wins

## Blockers

## Learning

## Next Steps
"""

    note_file.write_text(template.format(date=date_str), encoding="utf-8")
    console.print(f"[green]Reflection created for {date_str}[/green]")
    console.print(f"[dim]{note_file}[/dim]")
    return True
