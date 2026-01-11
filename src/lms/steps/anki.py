"""Anki step implementation using AnkiConnect API.

Provides a simple summary of decks and due cards, with optional sync.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests
from rich.console import Console
from rich.table import Table

console = Console()


def get_anki_url_from_env() -> str:
    """Return AnkiConnect URL from env or default."""
    return os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")


def anki_request(
    action: str, params: Optional[dict] = None, url: Optional[str] = None
) -> dict:
    """Send a request to AnkiConnect.

    Args:
        action: AnkiConnect action name
        params: Parameters for the action
        url: AnkiConnect base URL (defaults to env)

    Returns:
        Response JSON as dict; empty dict on error
    """
    if url is None:
        url = get_anki_url_from_env()
    payload = {"action": action, "version": 6}
    if params:
        payload["params"] = params

    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return {}


def get_deck_names(url: Optional[str] = None) -> List[str]:
    """Fetch deck names from AnkiConnect."""
    data = anki_request("deckNames", url=url)
    result = data.get("result")
    return result if isinstance(result, list) else []


def find_due_cards_for_deck(deck_name: str, url: Optional[str] = None) -> List[int]:
    """Return list of due card IDs for a given deck."""
    query = f"is:due deck:'{deck_name}'"
    data = anki_request("findCards", params={"query": query}, url=url)
    result = data.get("result")
    return result if isinstance(result, list) else []


def get_due_counts_by_deck(url: Optional[str] = None) -> Dict[str, int]:
    """Compute due card counts per deck."""
    counts: Dict[str, int] = {}
    for deck in get_deck_names(url=url):
        counts[deck] = len(find_due_cards_for_deck(deck, url=url))
    return counts


def anki_step() -> None:
    """Run the Anki step: show deck due counts and optionally sync."""
    url = get_anki_url_from_env()
    counts = get_due_counts_by_deck(url)

    if not counts:
        console.print("[yellow]No decks found or AnkiConnect unavailable.[/yellow]")
        return

    table = Table(title="Anki Decks - Due Cards")
    table.add_column("Deck", style="cyan", no_wrap=True)
    table.add_column("Due", style="magenta")

    total_due = 0
    for deck, due in counts.items():
        table.add_row(deck, str(due))
        total_due += due

    table.add_row("[bold]Total[/bold]", str(total_due))
    console.print(table)

    auto_sync = os.getenv("ANKI_AUTO_SYNC", "false").lower() in {"1", "true", "yes"}
    if auto_sync:
        resp = anki_request("sync", url=url)
        if "error" in resp and resp["error"]:
            console.print("[red]Anki sync error[/red]")
        else:
            console.print("[green]Anki synced successfully[/green]")
