"""Logging configuration and utilities for SkillOps."""

import logging
import sys


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for SkillOps.

    Args:
        verbose: If True, enable DEBUG level logging. Otherwise, INFO level.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )

    # Explicitly set root level so patched basicConfig still applies
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module name.

    Args:
        name: The module name (typically __name__).

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)
