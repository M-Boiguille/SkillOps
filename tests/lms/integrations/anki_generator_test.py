from src.lms.integrations.anki_generator import AnkiMarkdownGenerator
from src.lms.integrations.obsidian_scanner import Flashcard


def test_format_flashcard_tsv():
    card = Flashcard("What?", "Answer", tags=["test", "anki"])
    gen = AnkiMarkdownGenerator()

    formatted = gen.format_flashcard(card, separator="\t")
    assert "What?" in formatted
    assert "Answer" in formatted
    assert "test;anki" in formatted


def test_generate_deck_content_empty():
    gen = AnkiMarkdownGenerator()
    content = gen.generate_deck_content([])
    assert "Total cards: 0" in content


def test_generate_deck_content_with_cards():
    card1 = Flashcard("Q1", "A1", tags=["flashcard"])
    card2 = Flashcard("Q2", "A2", tags=["flashcard"])
    gen = AnkiMarkdownGenerator(deck_name="TestDeck")

    content = gen.generate_deck_content([card1, card2])
    assert "TestDeck" in content
    assert "Total cards: 2" in content
    assert "Q1" in content
    assert "Q2" in content


def test_generate_deck_file(tmp_path):
    card = Flashcard("Question?", "Answer!", tags=["test"])
    gen = AnkiMarkdownGenerator()
    deck_file = tmp_path / "deck.txt"

    success = gen.generate_deck_file([card], str(deck_file))
    assert success is True
    assert deck_file.exists()

    content = deck_file.read_text()
    assert "Question?" in content
    assert "Answer!" in content


def test_generate_deck_file_empty_list(tmp_path):
    gen = AnkiMarkdownGenerator()
    deck_file = tmp_path / "empty.txt"

    success = gen.generate_deck_file([], str(deck_file))
    assert success is False
