"""Tests for BooksManager class."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

import pytest
import yaml

from src.lms.books.manager import BooksManager, BookStatus


@pytest.fixture
def tmp_books_dir(tmp_path):
    """Create temporary books directory structure."""
    books_dir = tmp_path / "books"
    books_dir.mkdir()
    (books_dir / "pending").mkdir()
    (books_dir / "processing").mkdir()
    (books_dir / "completed").mkdir()
    return books_dir


@pytest.fixture
def manager(tmp_books_dir):
    """Create BooksManager with temporary directory."""
    return BooksManager(books_root=tmp_books_dir)


class TestBooksManagerInit:
    """Tests for BooksManager initialization."""

    def test_init_creates_directories(self, tmp_path):
        """Test that __init__ creates required directories."""
        books_dir = tmp_path / "books"
        manager = BooksManager(books_root=books_dir)

        assert (books_dir / "pending").exists()
        assert (books_dir / "processing").exists()
        assert (books_dir / "completed").exists()
        # Manifest path is set but not created until _save_manifest is called
        assert manager.manifest_path == books_dir / "books-manifest.yaml"

    def test_init_creates_default_manifest(self, manager):
        """Test that __init__ creates default manifest structure."""
        assert "version" in manager.manifest
        assert "books" in manager.manifest
        assert "statistics" in manager.manifest
        assert manager.manifest["books"] == []
        assert manager.manifest["statistics"]["total_books"] == 0


class TestManifestOperations:
    """Tests for manifest loading and saving."""

    def test_load_manifest_creates_if_missing(self, tmp_books_dir):
        """Test that missing manifest is created with defaults."""
        manager = BooksManager(books_root=tmp_books_dir)
        manifest = manager.manifest

        assert manifest["version"] == "1.0"
        assert manifest["statistics"]["total_books"] == 0

    def test_load_manifest_existing(self, tmp_books_dir):
        """Test loading existing manifest."""
        # Create manifest with sample data
        manifest_path = tmp_books_dir / "books-manifest.yaml"
        sample_manifest = {
            "version": "1.0",
            "books": [{"name": "test-book", "status": "pending"}],
            "statistics": {"total_books": 1}
        }
        with open(manifest_path, 'w') as f:
            yaml.dump(sample_manifest, f)

        manager = BooksManager(books_root=tmp_books_dir)
        assert len(manager.manifest["books"]) == 1
        assert manager.manifest["books"][0]["name"] == "test-book"

    def test_save_manifest(self, manager):
        """Test saving manifest to disk."""
        book_entry = {
            "name": "test-book",
            "status": BookStatus.PENDING,
            "pdf_path": "/path/to/test.pdf",
            "submitted_at": datetime.now().isoformat(),
            "batch_job_name": None,
            "completed_at": None,
            "estimated_completion": None,
            "imported_at": None,
            "results": {"zettelkasten": None, "flashcards": None, "pareto": None},
            "metadata": {"pages": None, "tokens_estimated": None, "cost_usd": None},
            "error": None
        }
        manager.manifest["books"].append(book_entry)
        manager._save_manifest()

        # Verify it's saved to disk
        with open(manager.manifest_path, 'r') as f:
            loaded = yaml.safe_load(f)

        assert len(loaded["books"]) == 1
        assert loaded["books"][0]["name"] == "test-book"


class TestBookOperations:
    """Tests for book entry operations."""

    def test_add_book(self, manager, tmp_path):
        """Test adding a new book to manifest."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        result = manager.add_book("test-book", pdf_path)

        assert result["name"] == "test-book"
        assert result["status"] == BookStatus.PENDING
        assert len(manager.manifest["books"]) == 1

    def test_add_book_duplicate_warning(self, manager, tmp_path, capsys):
        """Test adding duplicate book returns existing."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        result = manager.add_book("test-book", pdf_path)

        assert len(manager.manifest["books"]) == 1
        captured = capsys.readouterr()
        assert "already exists" in captured.out

    def test_get_book(self, manager, tmp_path):
        """Test getting book from manifest."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        book = manager.get_book("test-book")

        assert book is not None
        assert book["name"] == "test-book"

    def test_get_book_not_found(self, manager):
        """Test getting non-existent book returns None."""
        book = manager.get_book("nonexistent")
        assert book is None

    def test_update_book_status(self, manager, tmp_path):
        """Test updating book status."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager.update_book_status("test-book", BookStatus.PROCESSING, pages=240)

        book = manager.get_book("test-book")
        assert book["status"] == BookStatus.PROCESSING
        assert book["metadata"]["pages"] == 240

    def test_update_book_status_not_found(self, manager):
        """Test updating non-existent book raises error."""
        with pytest.raises(ValueError, match="not found"):
            manager.update_book_status("nonexistent", BookStatus.PROCESSING)


class TestStatisticsUpdate:
    """Tests for statistics tracking."""

    def test_update_statistics_counts(self, manager, tmp_path):
        """Test that statistics are correctly updated."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("book1", pdf_path)
        manager.add_book("book2", pdf_path)

        manager.update_book_status("book1", BookStatus.PROCESSING, cost_usd=0.005)
        manager.update_book_status("book2", BookStatus.COMPLETED, cost_usd=0.007)

        stats = manager.manifest["statistics"]
        assert stats["total_books"] == 2
        assert stats["processing"] == 1
        assert stats["completed"] == 1
        assert abs(stats["total_cost_usd"] - 0.012) < 0.0001

    def test_statistics_persist_after_save(self, manager, tmp_path):
        """Test that statistics are persisted to disk."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager._save_manifest()

        # Create new manager instance and verify stats
        new_manager = BooksManager(books_root=manager.books_root)
        assert new_manager.manifest["statistics"]["total_books"] == 1


class TestCreateBatchRequests:
    """Tests for batch request creation."""

    def test_create_batch_requests_structure(self, manager):
        """Test that batch requests have correct structure."""
        requests = manager._create_batch_requests("test-book", "files/test.pdf")

        assert len(requests) == 3
        assert all("key" in req for req in requests)
        assert all("request" in req for req in requests)

        # Check keys include output types
        keys = [req["key"] for req in requests]
        assert any("zettelkasten" in key for key in keys)
        assert any("flashcards" in key for key in keys)
        assert any("pareto" in key for key in keys)

    def test_batch_request_has_model_and_prompt(self, manager):
        """Test that batch requests have model and prompt."""
        requests = manager._create_batch_requests("test-book", "files/test.pdf")

        for req in requests:
            assert req["request"]["model"] == "gemini-2.0-flash-exp"
            assert "contents" in req["request"]
            assert "generationConfig" in req["request"]
            assert req["request"]["generationConfig"]["responseMimeType"] == "application/json"


class TestLoadPrompts:
    """Tests for prompt loading."""

    def test_load_prompts_fallback(self, manager):
        """Test fallback prompts when file doesn't exist."""
        prompts = manager._load_prompts()

        assert "zettelkasten" in prompts
        assert "flashcards" in prompts
        assert "pareto" in prompts
        assert len(prompts["zettelkasten"]) > 0

    def test_load_prompts_keys(self, manager):
        """Test that all required prompt types are present."""
        prompts = manager._load_prompts()

        required_types = {"zettelkasten", "flashcards", "pareto"}
        assert required_types.issubset(set(prompts.keys()))


class TestDisplayQueue:
    """Tests for queue display functionality."""

    def test_display_queue_empty(self, manager, capsys):
        """Test displaying empty queue."""
        manager.display_queue()

        captured = capsys.readouterr()
        assert "No books in queue" in captured.out

    def test_display_queue_with_books(self, manager, tmp_path, capsys):
        """Test displaying queue with books."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("book1", pdf_path)
        manager.add_book("book2", pdf_path)

        manager.update_book_status("book1", BookStatus.PROCESSING)
        manager.update_book_status("book2", BookStatus.COMPLETED)

        manager.display_queue()

        captured = capsys.readouterr()
        assert "book1" in captured.out
        assert "book2" in captured.out
        assert "Processing" in captured.out
        assert "Ready" in captured.out


class TestStatusTransitions:
    """Tests for book status transitions."""

    def test_status_pending_to_processing(self, manager, tmp_path):
        """Test transition from pending to processing."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager.update_book_status("test-book", BookStatus.PROCESSING)

        book = manager.get_book("test-book")
        assert book["status"] == BookStatus.PROCESSING

    def test_status_processing_to_completed(self, manager, tmp_path):
        """Test transition from processing to completed."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager.update_book_status("test-book", BookStatus.PROCESSING)
        manager.update_book_status("test-book", BookStatus.COMPLETED)

        book = manager.get_book("test-book")
        assert book["status"] == BookStatus.COMPLETED

    def test_status_to_failed(self, manager, tmp_path):
        """Test transition to failed status."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager.update_book_status("test-book", BookStatus.PROCESSING)
        manager.update_book_status("test-book", BookStatus.FAILED, error="Test error")

        book = manager.get_book("test-book")
        assert book["status"] == BookStatus.FAILED
        assert book["error"] == "Test error"


class TestMetadataUpdate:
    """Tests for metadata updates."""

    def test_update_cost_metadata(self, manager, tmp_path):
        """Test updating cost in metadata."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager.update_book_status("test-book", BookStatus.PROCESSING, cost_usd=0.0054)

        book = manager.get_book("test-book")
        assert book["metadata"]["cost_usd"] == 0.0054

    def test_update_pages_metadata(self, manager, tmp_path):
        """Test updating pages in metadata."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager.update_book_status("test-book", BookStatus.PROCESSING, pages=240)

        book = manager.get_book("test-book")
        assert book["metadata"]["pages"] == 240

    def test_update_timestamps(self, manager, tmp_path):
        """Test updating completion timestamps."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)

        now = datetime.now().isoformat()
        manager.update_book_status("test-book", BookStatus.COMPLETED, completed_at=now)

        book = manager.get_book("test-book")
        assert book["completed_at"] == now


class TestFetchBooksWithMocks:
    """Tests for fetch_completed_books with mocked API."""

    @patch("src.lms.books.manager.genai.Client")
    def test_fetch_completed_books_no_processing(self, mock_client_class, manager, capsys):
        """Test fetch when no books are processing."""
        manager.fetch_completed_books("fake-api-key")

        captured = capsys.readouterr()
        assert "No books currently processing" in captured.out

    @patch("src.lms.books.manager.genai.Client")
    def test_fetch_completed_books_with_specific_book(self, mock_client_class, manager, tmp_path, capsys):
        """Test fetch with specific book name."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        manager.add_book("test-book", pdf_path)
        manager.fetch_completed_books("fake-api-key", book_name="test-book")

        captured = capsys.readouterr()
        # Should show book not found or processing status
        assert "test-book" in captured.out or "No batch job" in captured.out


class TestImportBooksWithMocks:
    """Tests for import_books_to_vault with mocked file operations."""

    def test_import_books_no_completed(self, manager, capsys):
        """Test import when no books are completed."""
        manager.import_books_to_vault()

        captured = capsys.readouterr()
        assert "No completed books" in captured.out

    def test_import_books_creates_vault_directory(self, manager, tmp_path, capsys):
        """Test that import creates vault directory if missing."""
        vault_path = tmp_path / "vault"
        manager.import_books_to_vault(vault_path=str(vault_path))

        # Vault should be created
        assert vault_path.exists()


class TestCommandFunctions:
    """Tests for CLI command wrapper functions."""

    @patch("src.lms.books.manager.BooksManager")
    def test_check_books_command(self, mock_manager_class):
        """Test check_books_command calls display_queue."""
        from src.lms.books.manager import check_books_command

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        check_books_command()

        mock_manager.display_queue.assert_called_once()

    @patch("src.lms.books.manager.BooksManager")
    def test_submit_books_command_with_key(self, mock_manager_class):
        """Test submit_books_command with API key."""
        from src.lms.books.manager import submit_books_command

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        submit_books_command(api_key="test-key")

        mock_manager.submit_pending_books.assert_called_once_with("test-key")

    @patch("src.lms.books.manager.BooksManager")
    def test_submit_books_command_missing_key(self, mock_manager_class, capsys):
        """Test submit_books_command without API key shows error."""
        from src.lms.books.manager import submit_books_command

        with patch.dict("os.environ", {}, clear=True):
            submit_books_command(api_key=None)

        captured = capsys.readouterr()
        assert "GEMINI_API_KEY not found" in captured.out

    @patch("src.lms.books.manager.BooksManager")
    def test_fetch_books_command(self, mock_manager_class):
        """Test fetch_books_command calls fetch_completed_books."""
        from src.lms.books.manager import fetch_books_command

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        fetch_books_command(api_key="test-key", book_name="test-book")

        mock_manager.fetch_completed_books.assert_called_once_with("test-key", "test-book")

    @patch("src.lms.books.manager.BooksManager")
    def test_import_books_command(self, mock_manager_class):
        """Test import_books_command calls import_books_to_vault."""
        from src.lms.books.manager import import_books_command

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        import_books_command(vault_path="/vault", book_name="test-book")

        mock_manager.import_books_to_vault.assert_called_once_with("/vault", "test-book")
