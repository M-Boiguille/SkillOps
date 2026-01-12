from datetime import datetime
from unittest.mock import MagicMock, patch

from src.lms.steps.create import compute_file_hash, create_step


@patch("src.lms.steps.create.AnkiMarkdownGenerator")
@patch("src.lms.steps.create.ObsidianScanner")
def test_create_step_missing_vault_path(mock_scanner, mock_gen):
    with patch.dict("os.environ", {}, clear=True):
        success = create_step(vault_path=None)
        assert success is False
        mock_scanner.assert_not_called()


@patch("src.lms.steps.create.AnkiMarkdownGenerator")
@patch("src.lms.steps.create.ObsidianScanner")
def test_create_step_scan_failure(mock_scanner_class, mock_gen, tmp_path):
    mock_scanner_class.side_effect = ValueError("Vault not found")

    vault = tmp_path / "vault"
    vault.mkdir()

    success = create_step(vault_path=vault)
    assert success is False


@patch("src.lms.steps.create.AnkiMarkdownGenerator")
@patch("src.lms.steps.create.ObsidianScanner")
def test_create_step_no_flashcards(mock_scanner_class, mock_gen, tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()

    mock_scanner = MagicMock()
    mock_scanner.extract_all_flashcards.return_value = []
    mock_scanner_class.return_value = mock_scanner

    success = create_step(vault_path=vault)
    assert success is False


@patch("src.lms.steps.create.AnkiMarkdownGenerator")
@patch("src.lms.steps.create.ObsidianScanner")
def test_create_step_success(mock_scanner_class, mock_gen_class, tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    storage = tmp_path / "storage"
    storage.mkdir()
    anki_sync = tmp_path / "anki"
    anki_sync.mkdir()

    # Mock scanner
    mock_scanner = MagicMock()
    mock_card1 = MagicMock()
    mock_card2 = MagicMock()
    mock_scanner.extract_all_flashcards.return_value = [mock_card1, mock_card2]
    mock_scanner_class.return_value = mock_scanner

    # Mock generator
    mock_gen = MagicMock()
    mock_gen.generate_deck_file.return_value = True
    mock_gen_class.return_value = mock_gen

    success = create_step(
        vault_path=vault, storage_path=storage, anki_sync_path=anki_sync
    )

    assert success is True
    mock_scanner_class.assert_called_once()
    mock_gen.generate_deck_file.assert_called_once()


@patch("src.lms.steps.create.AnkiMarkdownGenerator")
@patch("src.lms.steps.create.ObsidianScanner")
def test_create_step_skips_when_deck_unchanged(
    mock_scanner_class, mock_gen_class, tmp_path
):
    vault = tmp_path / "vault"
    vault.mkdir()
    storage = tmp_path / "storage"
    storage.mkdir()
    anki_sync = tmp_path / "anki"
    anki_sync.mkdir()

    # Existing deck file with recorded hash
    today = datetime.now().strftime("%Y-%m-%d")
    deck_file = anki_sync / f"skillops-{today}.txt"
    deck_file.write_text("flashcards")

    hashes_file = storage / ".flashcard_hashes"
    existing_hash = compute_file_hash(deck_file)
    hashes_file.write_text(existing_hash + "\n")

    mock_scanner = MagicMock()
    mock_scanner.extract_all_flashcards.return_value = [MagicMock()]
    mock_scanner_class.return_value = mock_scanner

    mock_gen = MagicMock()
    mock_gen.generate_deck_file.return_value = True
    mock_gen_class.return_value = mock_gen

    success = create_step(
        vault_path=vault, storage_path=storage, anki_sync_path=anki_sync
    )

    assert success is True
    mock_gen.generate_deck_file.assert_not_called()
