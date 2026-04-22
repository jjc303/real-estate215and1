from __future__ import annotations

import logging
from pathlib import Path


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)


def ensure_log_dir(log_file_path: str) -> None:
    Path(log_file_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def setup_logging(app) -> None:
    log_file_path = app.config["LOG_FILE_PATH"]
    ensure_log_dir(log_file_path)

    log_level_name = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)

    app.logger.handlers.clear()
    app.logger.setLevel(log_level)
    app.logger.propagate = True

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers.clear()
    werkzeug_logger.setLevel(log_level)
    werkzeug_logger.propagate = True
