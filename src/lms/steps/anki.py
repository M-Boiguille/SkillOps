"""Quiz step using local SQLite cards (AnkiConnect removed)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from rich.console import Console
from rich.table import Table

from src.lms.database import get_connection, get_logical_date, init_db

console = Console()


def get_due_counts_by_topic(
    storage_path: Optional[Path] = None,
) -> Dict[str, int]:
    """Compute due card counts per topic from SQLite."""
    conn = get_connection(storage_path)
    cursor = conn.cursor()
    today = get_logical_date()
    cursor.execute(
        """
        SELECT topic, COUNT(*)
        FROM quiz_cards
        WHERE last_reviewed IS NULL OR date(last_reviewed) < ?
        GROUP BY topic
        """,
        (today,),
    )
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: int(row[1]) for row in rows}


def anki_step(storage_path: Optional[Path] = None) -> None:
    """Show due quiz cards per topic (local SQLite)."""
    init_db(storage_path=storage_path)
    counts = get_due_counts_by_topic(storage_path=storage_path)

    if not counts:
        console.print("[yellow]Aucune carte en attente.[/yellow]")
        return

    table = Table(title="Quiz - Cartes à revoir")
    table.add_column("Sujet", style="cyan", no_wrap=True)
    table.add_column("À revoir", style="magenta")

    total_due = 0
    for topic, due in counts.items():
        table.add_row(topic, str(due))
        total_due += due

    table.add_row("[bold]Total[/bold]", str(total_due))
    console.print(table)
