"""
app/utils/logger.py

Centralized logging configuration.

Why this exists as its own module:
    Every sprint from here on will add routes/services/repositories
    that need to log (info on requests, warnings on bad input, errors
    on failures). Rather than each file configuring its own logger,
    this module configures the app's root logger ONCE, from the
    factory, so `current_app.logger` (or any `logging.getLogger(...)`)
    behaves consistently everywhere: same format, same level, same
    destinations (console + file).

Two handlers are attached:
    - StreamHandler: prints to console, useful during local development
      with `python run.py`.
    - RotatingFileHandler: writes to logs/skillsync.log, capped in
      size with backups, so log files don't grow forever on a long-
      running dev server.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask

# Shared format for both handlers — includes timestamp, level, logger
# name (module), and message, which is enough to trace an issue back
# to its source file during debugging.
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Rotate at 1 MB per file, keep 5 backups — plenty for a dev/academic
# project; avoids unbounded log growth without needing external
# log-rotation tooling (explicitly out of scope per project constraints).
MAX_LOG_BYTES = 1 * 1024 * 1024
BACKUP_COUNT = 5


def configure_logging(app: Flask) -> None:
    """
    Attaches console and rotating-file handlers to the Flask app's
    logger, using LOG_LEVEL / LOG_DIR / LOG_FILE from app.config.

    Args:
        app: The Flask application instance being configured. Must
            already have its config loaded (i.e. called after
            app.config.from_object(...) in the factory).
    """
    log_level_name: str = app.config.get("LOG_LEVEL", "INFO")
    log_level: int = getattr(logging, log_level_name.upper(), logging.INFO)

    log_dir: str = app.config["LOG_DIR"]
    log_file: str = app.config["LOG_FILE"]

    # Ensure the logs/ directory exists before attaching a file handler
    # pointing into it (a fresh clone of the repo won't have it yet,
    # since log files themselves are gitignored — see .gitignore).
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Clear any default handlers Flask/Werkzeug may have attached,
    # to avoid duplicate log lines, then attach ours.
    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
