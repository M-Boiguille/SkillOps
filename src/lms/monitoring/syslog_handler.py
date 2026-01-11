"""Syslog integration for SkillOps logging."""

from __future__ import annotations

import logging
import logging.handlers


def setup_syslog_handler(
    app_name: str = "skillops",
    facility: str = "user",
    address: str = "/dev/log",
) -> logging.Logger:
    """Setup syslog handler for structured logging.

    Sends logs to system syslog, visible via journalctl (systemd)
    or grep syslog file.

    Args:
        app_name: Application name for syslog identification
        facility: Syslog facility (user, local0-local7, etc)
        address: Syslog socket address
                 (/dev/log on Linux, /var/run/syslog on macOS)

    Returns:
        Configured logger instance sending to syslog

    Example:
        logger = setup_syslog_handler('skillops')
        logger.error('Something went wrong')
        # View with: journalctl -u skillops | tail -20
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.DEBUG)

    # Map facility string to syslog facility
    facility_map = {
        "user": logging.handlers.SysLogHandler.LOG_USER,
        "local0": logging.handlers.SysLogHandler.LOG_LOCAL0,
        "local1": logging.handlers.SysLogHandler.LOG_LOCAL1,
        "local2": logging.handlers.SysLogHandler.LOG_LOCAL2,
        "local3": logging.handlers.SysLogHandler.LOG_LOCAL3,
        "local4": logging.handlers.SysLogHandler.LOG_LOCAL4,
        "local5": logging.handlers.SysLogHandler.LOG_LOCAL5,
        "local6": logging.handlers.SysLogHandler.LOG_LOCAL6,
        "local7": logging.handlers.SysLogHandler.LOG_LOCAL7,
    }

    syslog_facility = facility_map.get(
        facility, logging.handlers.SysLogHandler.LOG_USER
    )

    try:
        # Try to connect to syslog
        syslog_handler = logging.handlers.SysLogHandler(
            address=address,
            facility=syslog_facility,
        )

        # Format: include app name and severity for clarity
        formatter = logging.Formatter(
            f"{app_name}[%(process)d]: " "[%(levelname)s] %(name)s - %(message)s"
        )
        syslog_handler.setFormatter(formatter)
        logger.addHandler(syslog_handler)

        return logger

    except (OSError, Exception) as e:
        # Syslog not available (e.g., on some systems or containers)
        # Graceful fallback: return logger without syslog
        # (caller should add file handler if needed)
        logger.warning(f"Syslog not available ({e}): logging to stderr only")
        return logger


def get_syslog_logger(app_name: str = "skillops") -> logging.Logger:
    """Get or create syslog logger instance.

    Convenience function if syslog already configured elsewhere.

    Args:
        app_name: Application name
                  (must match setup_syslog_handler call)

    Returns:
        Logger configured for syslog
    """
    return logging.getLogger(app_name)
