"""Lightweight logger that writes to both stdout and file."""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path


def setup_logger(log_path: Path, verbose: bool = False) -> Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("soft_twitter")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

