"""
Logging configuration for the event manager

This module provides centralized logging configuration that works for both
CLI and TUI modes, with appropriate formatting and log levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> None:
    """
    Configure logging for the application
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file for persistent logging
        console_output: Whether to output logs to console
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    # Detailed format for file logging
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Simpler format for console
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler (if enabled)
    if console_output:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler (max 5MB, keep 3 backups)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for noisy third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('bs4').setLevel(logging.WARNING)
    
    logging.debug(f"Logging configured: level={level}, file={log_file}, console={console_output}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def configure_for_cli(debug: bool = False) -> None:
    """
    Configure logging for CLI mode
    
    Args:
        debug: Whether to enable debug logging
    """
    level = 'DEBUG' if debug else 'INFO'
    setup_logging(level=level, console_output=True)


def configure_for_tui(log_file: Optional[Path] = None) -> None:
    """
    Configure logging for TUI mode (minimal console output, log to file)
    
    Args:
        log_file: Path to log file (default: logs/event_manager.log)
    """
    if log_file is None:
        log_file = Path('logs') / 'event_manager.log'
    
    # In TUI mode, only show errors on console, log everything to file
    setup_logging(level='ERROR', log_file=log_file, console_output=True)


def configure_for_production() -> None:
    """
    Configure logging for production (minimal output, log warnings and above)
    """
    setup_logging(level='WARNING', console_output=True)


def configure_for_development(log_file: Optional[Path] = None) -> None:
    """
    Configure logging for development (verbose output, log to file)
    
    Args:
        log_file: Path to log file (default: logs/event_manager_dev.log)
    """
    if log_file is None:
        log_file = Path('logs') / 'event_manager_dev.log'
    
    setup_logging(level='DEBUG', log_file=log_file, console_output=True)
