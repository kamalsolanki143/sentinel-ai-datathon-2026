"""
Sentinel AI - Logging Configuration
=====================================
File: backend/config/logging_config.py
Purpose: Professional Loguru logging setup with file rotation, console coloring,
         and specialized log files for ML, AI, and APIs.

Dependencies: loguru
"""

import sys
from pathlib import Path
from loguru import logger
from backend.config.settings import get_settings

settings = get_settings()

# Define log paths
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

APP_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
AI_LOG_FILE = LOG_DIR / "ai_agents.log"
ML_LOG_FILE = LOG_DIR / "ml_models.log"

# Define log format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def setup_logging() -> None:
    """Configure Loguru logging for the Sentinel AI application."""
    # Remove default handler
    logger.remove()

    # Determine log level
    log_level = "DEBUG" if settings.DEBUG else "INFO"

    # Console Logger (Colored)
    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level=log_level,
        colorize=True,
        enqueue=True,
    )

    # General Application File Logger (Daily Rotation)
    logger.add(
        APP_LOG_FILE,
        format=LOG_FORMAT,
        level="INFO",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )

    # Error File Logger
    logger.add(
        ERROR_LOG_FILE,
        format=LOG_FORMAT,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Specific AI Agents Logger
    logger.add(
        AI_LOG_FILE,
        format=LOG_FORMAT,
        level="DEBUG",
        rotation="10 MB",
        retention="14 days",
        filter=lambda record: "backend.agents" in record["name"],
        enqueue=True,
    )

    # Specific ML Models Logger
    logger.add(
        ML_LOG_FILE,
        format=LOG_FORMAT,
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        filter=lambda record: "ml." in record["name"],
        enqueue=True,
    )

    # Forward standard logging to Loguru
    import logging
    
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Replace basic logging with InterceptHandler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Optional: silence noisy loggers
    for _logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        logging_logger = logging.getLogger(_logger_name)
        logging_logger.handlers = [InterceptHandler()]
        
    logger.info("Logging configured successfully.")
