"""Logging configuration using loguru."""
import sys
from loguru import logger
import os


def setup_logger():
    """
    Configure the application logger with appropriate formatting and handlers.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")

    # Remove default handler
    logger.remove()

    # Add custom handler with formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler for errors
    logger.add(
        "logs/error.log",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    return logger


def get_logger(name: str):
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
