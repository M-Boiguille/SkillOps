"""Obsidian vault scanner for flashcard extraction."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class Flashcard:
    """Represent a single flashcard."""

    def __init__(self, question: str, answer: str, tags: Optional[list[str]] = None):
        self.question = question.strip()
        self.answer = answer.strip()
        self.tags = tags or []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Flashcard):
            return NotImplemented
        return (
            self.question == other.question
            and self.answer == other.answer
            and self.tags == other.tags
        )

    def __repr__(self) -> str:
        return f"Flashcard(q='{self.question[:30]}...', a='{self.answer[:30]}...')"


class ObsidianScanner:
    """Scanner for Obsidian vault to extract flashcards."""

    # Patterns for flashcard detection
    PATTERN_Q_A = re.compile(
        r"^[Qq]:\s*(.+?)\n[Aa]:\s*(.+?)(?:\n|$)", re.MULTILINE | re.DOTALL
    )
    PATTERN_Q_COLON_A = re.compile(
        r"^Q::\s*(.+?)\n?A::\s*(.+?)(?:\n|$)", re.MULTILINE | re.DOTALL
    )
    PATTERN_INLINE = re.compile(r"^(.+?)::\s*(.+?)$", re.MULTILINE)

    def __init__(self, vault_path: Optional[str] = None):
        if not vault_path:
            raise ValueError("vault_path is required")
        self.vault_path = Path(vault_path).expanduser().absolute()
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")
        if not self.vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {self.vault_path}")

    def scan_vault(self) -> list[Path]:
        """Recursively scan vault for markdown files.

        Returns:
            List of Path objects for all .md files in vault.
        """
        return list(self.vault_path.rglob("*.md"))

    def extract_flashcards_from_file(self, file_path: Path) -> list[Flashcard]:
        """Extract flashcards from a single markdown file.

        Args:
            file_path: Path to markdown file.

        Returns:
            List of Flashcard objects found in the file.
        """
        if not file_path.exists():
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        flashcards = []

        # Check if file has #flashcard tag
        if "#flashcard" not in content.lower():
            return []

        # Extract Q:/A: format
        for match in self.PATTERN_Q_A.finditer(content):
            q, a = match.groups()
            flashcards.append(Flashcard(q, a, tags=["flashcard"]))

        # Extract Q::A:: format
        for match in self.PATTERN_Q_COLON_A.finditer(content):
            q, a = match.groups()
            flashcards.append(Flashcard(q, a, tags=["flashcard"]))

        # Extract inline :: format (but avoid duplicates with above)
        for match in self.PATTERN_INLINE.finditer(content):
            q, a = match.groups()
            card = Flashcard(q, a, tags=["flashcard"])
            if card not in flashcards:
                flashcards.append(card)

        return flashcards

    def extract_all_flashcards(self) -> list[Flashcard]:
        """Extract all flashcards from vault.

        Returns:
            List of all Flashcard objects found in the vault.
        """
        files = self.scan_vault()
        flashcards = []

        for file_path in files:
            try:
                cards = self.extract_flashcards_from_file(file_path)
                flashcards.extend(cards)
            except Exception as e:
                console.print(f"[warning]Warning scanning {file_path}: {e}[/warning]")

        return flashcards
