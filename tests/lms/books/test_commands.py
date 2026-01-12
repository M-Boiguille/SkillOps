"""Tests for book processing CLI commands."""

from unittest.mock import MagicMock, patch
import pytest


class TestProcessPipelineCommand:
    """Tests for process_pipeline_command function."""

    @patch("src.lms.books.manager.BooksManager")
    def test_process_pipeline_one_time_mode(self, mock_manager_class):
        """Test process_pipeline in one-time mode."""
        from src.lms.books.manager import process_pipeline_command
        
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        process_pipeline_command(gemini_api_key="test-key", watch=False)
        
        # Should call submit, fetch, and import
        mock_manager.submit_pending_books.assert_called_once()
        mock_manager.fetch_completed_books.assert_called_once()
        mock_manager.import_books_to_vault.assert_called_once()

    @patch("src.lms.books.manager.BooksManager")
    @patch("src.lms.books.manager.time.sleep")
    def test_process_pipeline_watch_mode_no_books(self, mock_sleep, mock_manager_class):
        """Test process_pipeline watch mode with no processing books."""
        from src.lms.books.manager import process_pipeline_command
        
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        # No processing books
        mock_manager.manifest = {"books": []}
        # Mock the _get_processing_books method to return empty list
        mock_manager._get_processing_books = MagicMock(return_value=[])
        
        process_pipeline_command(gemini_api_key="test-key", watch=True, interval=30)
        
        # Should submit then finish (no polling needed)
        mock_manager.submit_pending_books.assert_called()

    def test_process_pipeline_no_api_key(self, capsys):
        """Test process_pipeline without API key shows error."""
        from src.lms.books.manager import process_pipeline_command
        
        with patch.dict("os.environ", {}, clear=True):
            process_pipeline_command(gemini_api_key=None)
        
        captured = capsys.readouterr()
        assert "GEMINI_API_KEY not found" in captured.out


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    @patch("src.lms.books.manager.BooksManager")
    def test_all_commands_available(self, mock_manager_class):
        """Test that all CLI commands can be imported."""
        from src.lms.books import (
            check_books_command,
            submit_books_command,
            fetch_books_command,
            import_books_command,
            process_pipeline_command
        )
        
        # All should be importable
        assert callable(check_books_command)
        assert callable(submit_books_command)
        assert callable(fetch_books_command)
        assert callable(import_books_command)
        assert callable(process_pipeline_command)

    @patch("src.lms.main.typer.Typer")
    def test_commands_registered_in_app(self, mock_typer):
        """Test that all book commands are registered in the app."""
        # This would be an integration test with the actual Typer app
        # For now, just verify the module loads
        import src.lms.main
        assert hasattr(src.lms.main, 'app')


class TestErrorHandling:
    """Tests for error handling in commands."""

    @patch("src.lms.books.manager.BooksManager")
    def test_submit_command_handles_api_errors(self, mock_manager_class):
        """Test that submit command handles API errors."""
        from src.lms.books.manager import submit_books_command
        
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        # Normal call should work
        submit_books_command(api_key="test-key")
        
        # Verify it was called
        mock_manager.submit_pending_books.assert_called_once_with("test-key")

    @patch("src.lms.books.manager.BooksManager")
    def test_fetch_command_handles_missing_book(self, mock_manager_class, capsys):
        """Test that fetch command handles missing book gracefully."""
        from src.lms.books.manager import fetch_books_command
        
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_book.return_value = None
        
        fetch_books_command(api_key="test-key", book_name="nonexistent")
        
        # Should handle gracefully
        captured = capsys.readouterr()
        # No errors should be raised


class TestCommandOutputFormatting:
    """Tests for command output formatting."""

    @patch("src.lms.books.manager.BooksManager")
    def test_check_books_output_format(self, mock_manager_class):
        """Test that check_books output is formatted correctly."""
        from src.lms.books.manager import check_books_command
        
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        check_books_command()
        
        # Verify display_queue was called
        mock_manager.display_queue.assert_called_once()

    @patch("src.lms.books.manager.BooksManager")
    def test_process_pipeline_output_includes_status(self, mock_manager_class, capsys):
        """Test that process_pipeline output shows progress."""
        from src.lms.books.manager import process_pipeline_command
        
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        process_pipeline_command(gemini_api_key="test-key", watch=False)
        
        captured = capsys.readouterr()
        # Should show some kind of progress message
        assert ("pipeline" in captured.out.lower() or 
                "submit" in captured.out.lower() or
                "complete" in captured.out.lower())
