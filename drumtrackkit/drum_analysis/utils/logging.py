#!/usr/bin/env python3
"""
Logging utility module for drum_analysis framework.
Provides a consistent logging interface across all components.
"""

import os
import logging
from typing import Optional, Dict, Any

# Default log levels based on environment or configuration
DEFAULT_LOG_LEVEL = os.environ.get('DRUM_ANALYSIS_LOG_LEVEL', 'INFO').upper()

# Set up a formatter that includes timestamp, logger name, level and message
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Log level mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def get_logger(name: str, level: Optional[str] = None,
               format_str: Optional[str] = None,
               log_to_file: bool = False,
               log_file: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger with the specified name.

    Args:
        name: The name of the logger, typically the module name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Custom format string for log messages
        log_to_file: Whether to log to a file in addition to console
        log_file: Path to log file if log_to_file is True

    Returns:
        A configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)

    # Set level from parameter, env var, or default to INFO
    if level is None:
        level = DEFAULT_LOG_LEVEL

    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Only add handlers if they don't exist to avoid duplicate handlers
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Set formatter
        formatter = logging.Formatter(format_str or DEFAULT_FORMAT)
        console_handler.setFormatter(formatter)

        # Add to logger
        logger.addHandler(console_handler)

        # Add file handler if requested
        if log_to_file:
            file_path = log_file or os.path.join(os.getcwd(), 'drum_analysis.log')
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def configure_root_logger(level: str = 'INFO',
                          format_str: Optional[str] = None,
                          log_to_file: bool = False,
                          log_file: Optional[str] = None) -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Custom format string for log messages
        log_to_file: Whether to log to a file in addition to console
        log_file: Path to log file if log_to_file is True
    """
    # Configure root logger
    root_logger = get_logger('drum_analysis', level, format_str, log_to_file, log_file)

    # Make it propagate to root
    root_logger.propagate = True


def configure_logging_from_config(config: Dict[str, Any]) -> None:
    """
    Configure logging system from a configuration dictionary.

    Args:
        config: Dictionary containing logging configuration
    """
    log_config = config.get('logging', {})

    # Configure root logger
    configure_root_logger(
        level=log_config.get('level', 'INFO'),
        format_str=log_config.get('format'),
        log_to_file=log_config.get('log_to_file', False),
        log_file=log_config.get('log_file')
    )

    # Configure specific loggers if defined
    specific_loggers = log_config.get('loggers', {})
    for logger_name, logger_config in specific_loggers.items():
        get_logger(
            name=logger_name,
            level=logger_config.get('level'),
            format_str=logger_config.get('format'),
            log_to_file=logger_config.get('log_to_file', False),
            log_file=logger_config.get('log_file')
        )