"""Anki markdown deck generator."""

from __future__ import annotations

from datetime import datetime

from src.lms.integrations.obsidian_scanner import Flashcard


class AnkiMarkdownGenerator:
    """Generate Anki-compatible markdown deck from flashcards."""

    def __init__(self, deck_name: str = "SkillOps"):
        self.deck_name = deck_name
        self.generated_at = datetime.now().isoformat()

    def format_flashcard(self, flashcard: Flashcard, separator: str = "\t") -> str:
        """Format a single flashcard for Anki import.

        Anki CSV/TSV format: question\tanswer\ttags

        Args:
            flashcard: Flashcard object.
            separator: Field separator (tab for TSV, comma for CSV).

        Returns:
            Formatted line for Anki import.
        """
        tags = ";".join(flashcard.tags) if flashcard.tags else ""
        # Escape newlines in question/answer for Anki compatibility
        question = flashcard.question.replace("\n", " ")
        answer = flashcard.answer.replace("\n", " ")
        return f"{question}{separator}{answer}{separator}{tags}"

    def generate_deck_content(
        self, flashcards: list[Flashcard], format_type: str = "tsv"
    ) -> str:
        """Generate full deck markdown content.

        Args:
            flashcards: List of Flashcard objects.
            format_type: 'tsv' for tab-separated, 'csv' for comma-separated.

        Returns:
            Markdown deck content ready for Anki import.
        """
        separator = "\t" if format_type == "tsv" else ","

        lines = [
            f"# {self.deck_name}",
            f"# Generated: {self.generated_at}",
            f"# Total cards: {len(flashcards)}",
            "#",
        ]

        for card in flashcards:
            lines.append(self.format_flashcard(card, separator))

        return "\n".join(lines) + "\n"

    def generate_deck_file(
        self, flashcards: list[Flashcard], file_path: str, format_type: str = "tsv"
    ) -> bool:
        """Generate and save deck file.

        Args:
            flashcards: List of Flashcard objects.
            file_path: Path where to save the deck file.
            format_type: 'tsv' or 'csv'.

        Returns:
            True if successful, False otherwise.
        """
        if not flashcards:
            return False

        try:
            content = self.generate_deck_content(flashcards, format_type)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except OSError:
            return False
