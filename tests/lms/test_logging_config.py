"""Tests for logging configuration and verbose mode."""

import logging
from io import StringIO
from unittest.mock import patch

from src.lms.logging_config import setup_logging, get_logger


class TestLoggingSetup:
    """Test logging configuration."""

    def test_setup_logging_verbose_sets_debug_level(self) -> None:
        """Test that verbose mode sets DEBUG level."""
        with patch("src.lms.logging_config.logging.basicConfig") as mock_config:
            setup_logging(verbose=True)
            # Get the level argument passed to basicConfig
            call_kwargs = mock_config.call_args[1]
            assert call_kwargs["level"] == logging.DEBUG

    def test_setup_logging_non_verbose_sets_info_level(self) -> None:
        """Test that non-verbose mode sets INFO level."""
        with patch("src.lms.logging_config.logging.basicConfig") as mock_config:
            setup_logging(verbose=False)
            call_kwargs = mock_config.call_args[1]
            assert call_kwargs["level"] == logging.INFO

    def test_setup_logging_configures_stream_handler(self) -> None:
        """Test that setup_logging configures a StreamHandler."""
        with patch("src.lms.logging_config.logging.basicConfig") as mock_config:
            setup_logging(verbose=True)
            call_kwargs = mock_config.call_args[1]
            # Verify StreamHandler is in handlers list
            handlers = call_kwargs["handlers"]
            assert len(handlers) > 0
            assert isinstance(handlers[0], logging.StreamHandler)

    def test_setup_logging_reduces_library_noise(self) -> None:
        """Test that setup_logging reduces noise from third-party libraries."""
        with patch("src.lms.logging_config.logging.getLogger") as mock_get_logger:
            setup_logging(verbose=True)
            # Verify library loggers are muted
            names = [
                c.args[0] if c.args else "" for c in mock_get_logger.call_args_list
            ]
            assert "urllib3" in names
            assert "requests" in names

    def test_setup_logging_default_is_non_verbose(self) -> None:
        """Test that setup_logging defaults to non-verbose."""
        with patch("src.lms.logging_config.logging.basicConfig") as mock_config:
            setup_logging()
            call_kwargs = mock_config.call_args[1]
            assert call_kwargs["level"] == logging.INFO


class TestGetLogger:
    """Test logger retrieval."""

    def test_get_logger_returns_logger_instance(self) -> None:
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_uses_provided_name(self) -> None:
        """Test that get_logger uses the provided module name."""
        logger = get_logger("test.module.name")
        assert logger.name == "test.module.name"

    def test_get_logger_returns_same_logger_for_same_name(self) -> None:
        """Test that get_logger returns same logger for repeated calls."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        assert logger1 is logger2

    def test_get_logger_logs_at_correct_level(self) -> None:
        """Test that logger logs at appropriate level."""
        with patch("src.lms.logging_config.logging.basicConfig"):
            setup_logging(verbose=True)
            logger = get_logger("test_module")
            # Logger should be able to log at debug level
            assert logger.isEnabledFor(logging.DEBUG)


class TestVerboseLoggingIntegration:
    """Test integration of verbose logging with main CLI."""

    def test_verbose_flag_enables_debug_output(self) -> None:
        """Test that --verbose flag enables debug logging."""
        with patch("src.lms.logging_config.setup_logging") as mock_setup:
            from src.lms import main

            # Simulate verbose flag
            with patch("src.lms.main.main_menu") as mock_menu:
                mock_menu.return_value = None
                with patch("src.lms.main.execute_step"):
                    with patch("src.lms.main.pagerduty_check") as mock_pagerduty:
                        mock_pagerduty.return_value = True
                        main.start(verbose=True)
            # Verify setup_logging was called with verbose=True
            mock_setup.assert_called_with(verbose=True)

    def test_verbose_flag_not_set_uses_default(self) -> None:
        """Test that without --verbose flag, default logging is used."""
        with patch("src.lms.logging_config.setup_logging") as mock_setup:
            from src.lms import main

            with patch("src.lms.main.main_menu") as mock_menu:
                mock_menu.return_value = None
                with patch("src.lms.main.execute_step"):
                    with patch("src.lms.main.pagerduty_check") as mock_pagerduty:
                        mock_pagerduty.return_value = True
                        main.start(verbose=False)
            # Verbose setup should not be called
            mock_setup.assert_not_called()

    def test_logger_debug_messages_in_verbose_mode(self) -> None:
        """Test that debug messages appear in verbose mode."""
        with patch("src.lms.logging_config.logging.basicConfig"):
            setup_logging(verbose=True)
            logger = get_logger("test_module")

            # Create a handler to capture log output
            stream = StringIO()
            handler = logging.StreamHandler(stream)
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)

            logger.debug("Test debug message")
            log_output = stream.getvalue()
            assert "Test debug message" in log_output

    def test_logger_respects_level_filtering(self) -> None:
        """Test that logger respects log level filtering."""
        with patch("src.lms.logging_config.logging.basicConfig"):
            setup_logging(verbose=False)
            logger = get_logger("test_module")
            logger.setLevel(logging.INFO)

            # Debug message should not be emitted at INFO level
            stream = StringIO()
            handler = logging.StreamHandler(stream)
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)

            logger.debug("Debug message")
            logger.info("Info message")
            log_output = stream.getvalue()

            assert "Debug message" not in log_output
            assert "Info message" in log_output
