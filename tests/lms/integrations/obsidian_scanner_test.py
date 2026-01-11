import pytest

from src.lms.integrations.obsidian_scanner import Flashcard, ObsidianScanner


def test_flashcard_equality():
    card1 = Flashcard("Q", "A", tags=["test"])
    card2 = Flashcard("Q", "A", tags=["test"])
    assert card1 == card2


def test_obsidian_scanner_requires_vault_path():
    with pytest.raises(ValueError):
        ObsidianScanner(vault_path=None)


def test_obsidian_scanner_validates_path_exists(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()

    scanner = ObsidianScanner(str(vault))
    assert scanner.vault_path == vault


def test_obsidian_scanner_scan_vault_empty(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()

    scanner = ObsidianScanner(str(vault))
    files = scanner.scan_vault()
    assert files == []


def test_obsidian_scanner_scan_vault_with_files(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "note1.md").write_text("content")
    (vault / "note2.md").write_text("content")
    subdir = vault / "sub"
    subdir.mkdir()
    (subdir / "note3.md").write_text("content")

    scanner = ObsidianScanner(str(vault))
    files = scanner.scan_vault()
    assert len(files) == 3


def test_extract_flashcards_from_file_q_a_format(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    note_file = vault / "flashcards.md"
    note_file.write_text(
        """# My Notes

Q: What is Docker?
A: A containerization platform

#flashcard
Q: What is Kubernetes?
A: Container orchestration system
"""
    )

    scanner = ObsidianScanner(str(vault))
    cards = scanner.extract_flashcards_from_file(note_file)
    assert len(cards) == 2
    assert cards[0].question == "What is Docker?"
    assert cards[1].question == "What is Kubernetes?"


def test_extract_flashcards_ignores_files_without_tag(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    note_file = vault / "notes.md"
    note_file.write_text(
        """Q: What is Docker?
A: A containerization platform
"""
    )

    scanner = ObsidianScanner(str(vault))
    cards = scanner.extract_flashcards_from_file(note_file)
    assert len(cards) == 0


def test_extract_all_flashcards(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "file1.md").write_text("#flashcard\nQ: Q1\nA: A1\n")
    (vault / "file2.md").write_text("#flashcard\nQ: Q2\nA: A2\n")

    scanner = ObsidianScanner(str(vault))
    cards = scanner.extract_all_flashcards()
    assert len(cards) == 2
