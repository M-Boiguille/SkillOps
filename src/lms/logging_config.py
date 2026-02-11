"""Logging configuration and utilities for SkillOps."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(verbose: bool = False, log_format: str | None = None) -> None:
    """Configure logging for SkillOps.

    Args:
        verbose: If True, enable DEBUG level logging. Otherwise, INFO level.
    """
    level = logging.DEBUG if verbose else logging.INFO

    resolved_format = (log_format or os.getenv("SKILLOPS_LOG_FORMAT", "text")).lower()
    handler = logging.StreamHandler(sys.stderr)
    if resolved_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    logging.basicConfig(level=level, handlers=[handler])

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
