"""
Structured logging module for Mint PDF.
Provides rotating file logs, split level routing, and clean, traceback-masked console warnings.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Default log settings
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "mint_pdf.log"
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 5  # Keep up to 5 history logs


def setup_logger(name: str = "mint_pdf", level: int = logging.DEBUG) -> logging.Logger:
    """
    Sets up a production-ready logger with a rotating file handler (detailed logs)
    and a custom clean console stream handler (warning/error only).
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Ensure log directory exists
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create log directory {LOG_DIR}: {e}")
        log_path = Path("mint_pdf.log")
    else:
        log_path = LOG_FILE

    # Formatter for the log file (includes filename, line numbers, and timestamps)
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s"
    )

    # Rotating File Handler (captures all logs from DEBUG to CRITICAL)
    try:
        file_handler = RotatingFileHandler(
            log_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not configure file logging: {e}")

    # Console Handler for user visible issues (Warnings/Errors only, no raw tracebacks)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter("[!] %(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def log_exception(
    e: Exception, user_msg: str, logger_instance: Optional[logging.Logger] = None
) -> None:
    """
    Logs a full stack trace to the log file for developers,
    but prints only a clean, user-friendly message to the console.

    Args:
        e: The caught exception.
        user_msg: A friendly, easy-to-understand description of what went wrong.
        logger_instance: Optional logger instance to use.
    """
    log = logger_instance or logger
    # Log the full traceback to file
    log.error(f"{user_msg} | System Error: {e}", exc_info=True)


# Initialize global logger
logger = setup_logger()
