"""Create step - Generate flashcards from Obsidian notes."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from src.lms.integrations.anki_generator import AnkiMarkdownGenerator
from src.lms.integrations.obsidian_scanner import ObsidianScanner

console = Console()


def get_storage_path() -> Path:
    """Return storage path from environment or default location."""
    storage_path_str = os.getenv(
        "STORAGE_PATH", str(Path.home() / ".local/share/skillops")
    )
    return Path(storage_path_str).expanduser().absolute()


def get_vault_path() -> Optional[Path]:
    """Return Obsidian vault path from environment."""
    vault_str = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    if not vault_str:
        return None
    return Path(vault_str).expanduser().absolute()


def get_anki_sync_path() -> Path:
    """Return Anki sync path from environment or default."""
    anki_str = os.getenv("ANKI_SYNC_PATH", "").strip()
    if anki_str:
        return Path(anki_str).expanduser().absolute()
    # Default Anki2 collection path
    return Path.home() / "Anki2" / "User 1" / "collection.media"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file for deduplication."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
    except OSError:
        return ""
    return sha256.hexdigest()


def create_step(
    storage_path: Optional[Path] = None,
    vault_path: Optional[Path] = None,
    anki_sync_path: Optional[Path] = None,
) -> bool:
    """Execute the Create step - generate flashcards from Obsidian.

    Args:
        storage_path: Custom storage directory.
        vault_path: Custom Obsidian vault path.
        anki_sync_path: Custom Anki sync path.

    Returns:
        True if successful, False otherwise.
    """
    console.print("\n[bold cyan]Create - Flashcard Generation[/bold cyan]\n")

    # Get paths
    storage_dir = storage_path or get_storage_path()
    vault_dir = vault_path or get_vault_path()

    if not vault_dir:
        console.print(
            "[red]OBSIDIAN_VAULT_PATH not configured.[/red]\n"
            "[yellow]Set OBSIDIAN_VAULT_PATH=<path/to/vault> in .env or use --vault-path[/yellow]\n"
        )
        return False

    anki_dir = anki_sync_path or get_anki_sync_path()
    anki_dir.mkdir(parents=True, exist_ok=True)

    # Scan and extract
    try:
        console.print(f"[dim]Scanning vault: {vault_dir}[/dim]")
        scanner = ObsidianScanner(str(vault_dir))
        flashcards = scanner.extract_all_flashcards()
    except ValueError as e:
        console.print(f"[red]Vault scan failed: {e}[/red]\n")
        return False

    if not flashcards:
        console.print(
            "[yellow]No flashcards found (look for #flashcard tag).[/yellow]\n"
        )
        return False

    # Prepare storage and dedupe tracking before writing files
    storage_dir.mkdir(parents=True, exist_ok=True)
    hashes_file = storage_dir / ".flashcard_hashes"
    existing_hashes = set()
    if hashes_file.exists():
        try:
            existing_hashes = set(hashes_file.read_text().strip().split("\n"))
        except OSError:
            pass

    generator = AnkiMarkdownGenerator(deck_name="SkillOps")
    today = datetime.now().strftime("%Y-%m-%d")
    deck_file = anki_dir / f"skillops-{today}.txt"

    # If today's deck already exists with a known hash, skip regeneration
    if deck_file.exists():
        existing_hash = compute_file_hash(deck_file)
        if existing_hash and existing_hash in existing_hashes:
            console.print(
                "[yellow]Flashcards unchanged from last generation.[/yellow]\n"
            )
            return True

    if not generator.generate_deck_file(flashcards, str(deck_file), format_type="tsv"):
        console.print(f"[red]Failed to write deck file: {deck_file}[/red]\n")
        return False

    # Check for duplicates
    deck_hash = compute_file_hash(deck_file)

    if deck_hash in existing_hashes:
        console.print("[yellow]Flashcards unchanged from last generation.[/yellow]\n")
        return True

    # Save hash
    try:
        with open(hashes_file, "a") as f:
            f.write(deck_hash + "\n")
    except OSError:
        pass

    console.print(
        f"[green]✓ Generated {len(flashcards)} flashcards[/green]\n"
        f"[green]✓ Saved to: {deck_file}[/green]\n"
        "[dim]Import this file into Anki using File -> Import[/dim]\n"
    )

    return True
