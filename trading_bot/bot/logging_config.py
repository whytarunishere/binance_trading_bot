"""Logging configuration.

Creates a logger named `trading_bot` with a file handler (detailed INFO+)
and a concise console handler (WARNING+). Keep console output readable
while preserving full request/response traces in the log file.
"""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_dir: Path | str = "logs") -> logging.Logger:
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    if logger.handlers:
        # If already configured, return existing logger (idempotent)
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    # File formatter includes timestamp and logger name for diagnostics
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path / "trading_bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console should be concise to avoid noisy stacktraces; file keeps full details.
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
