"""
Logging configuration.

Supports two output modes controlled by the LOG_JSON setting:
  - LOG_JSON=false  →  human-readable coloured logs (development)
  - LOG_JSON=true   →  structured JSON logs (production / log aggregators)

Usage:
    from app.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened", extra={"user_id": "usr_123"})
"""

import logging
import logging.config
import sys
from typing import Any

# Colour codes for human-readable output (only applied in non-JSON mode)
_RESET = "\033[0m"
_COLOURS: dict[str, str] = {
    "DEBUG": "\033[36m",     # cyan
    "INFO": "\033[32m",      # green
    "WARNING": "\033[33m",   # yellow
    "ERROR": "\033[31m",     # red
    "CRITICAL": "\033[35m",  # magenta
}


class _ColourFormatter(logging.Formatter):
    """Adds ANSI colour codes to the level name when writing to a TTY."""

    _FORMAT = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
    _DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        colour = _COLOURS.get(record.levelname, _RESET)
        record.levelname = f"{colour}{record.levelname}{_RESET}"
        formatter = logging.Formatter(self._FORMAT, datefmt=self._DATE_FORMAT)
        return formatter.format(record)


class _JSONFormatter(logging.Formatter):
    """Emits one JSON object per log line — suitable for log aggregation pipelines."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        import traceback

        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Merge any extra fields the caller passed in
        for key, value in record.__dict__.items():
            if key not in {
                "args", "asctime", "created", "exc_info", "exc_text",
                "filename", "funcName", "id", "levelname", "levelno",
                "lineno", "message", "module", "msecs", "msg", "name",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "taskName", "thread", "threadName",
            }:
                payload[key] = value

        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO", use_json: bool = False) -> None:
    """
    Set up application-wide logging.

    Call this once at startup (from app/main.py) before any loggers are used.

    Args:
        level:    Python log level string, e.g. "INFO", "DEBUG".
        use_json: When True, emit JSON-formatted log lines.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JSONFormatter() if use_json else _ColourFormatter())

    # Remove any handlers that may have been added by 3rd-party imports
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "watchfiles.main", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Promote uvicorn error logs to the root handler so they appear in our format
    logging.getLogger("uvicorn.error").propagate = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.

    Args:
        name: Typically ``__name__`` from the calling module.

    Returns:
        A standard :class:`logging.Logger` instance.
    """
    return logging.getLogger(name)
