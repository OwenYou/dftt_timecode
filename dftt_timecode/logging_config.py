"""
Logging configuration for DFTT Timecode library.

Automatically adjusts log level based on development context:
- **Installed packages** (from PyPI/build): INFO level (production default)
- **Main branch**: INFO level (production-ready code after PR)
- **Development branches** (dev, feature/*): DEBUG level (detailed tracing)

The logging level can be overridden with the DFTT_LOG_LEVEL environment variable.

Example:
    # Use default log level (INFO for installed packages, branch-dependent for development)
    from dftt_timecode import DfttTimecode
    tc = DfttTimecode('01:00:00:00', fps=24)

    # Override log level via environment variable
    import os
    os.environ['DFTT_LOG_LEVEL'] = 'WARNING'

    # Or configure programmatically
    import logging
    from dftt_timecode import configure_logging
    configure_logging(logging.DEBUG)
"""

import logging
import os
import subprocess
from typing import Optional


def _get_git_branch() -> Optional[str]:
    """
    Get the current git branch name.

    Returns:
        str: The current branch name, or None if not in a git repo or error occurs.
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=2,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return None


def _determine_log_level() -> int:
    """
    Determine the appropriate log level based on environment and git branch.

    Priority:
    1. DFTT_LOG_LEVEL environment variable (if set)
    2. DEBUG for development branches (dev, feature/*, etc.)
    3. INFO for main branch OR when git info unavailable (built packages)

    The default for built/installed packages is INFO to avoid verbose output
    in production environments.

    Returns:
        int: logging level constant (logging.DEBUG, logging.INFO, etc.)
    """
    # Check environment variable first (highest priority)
    env_level = os.environ.get('DFTT_LOG_LEVEL', '').upper()
    if env_level:
        level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        if env_level in level_mapping:
            return level_mapping[env_level]

    # Check git branch
    branch = _get_git_branch()

    if branch is None:
        # No git info available (e.g., installed package from PyPI)
        # Default to INFO for production use
        return logging.INFO
    elif branch == 'main':
        # Main branch: production-ready code after PR
        return logging.INFO
    else:
        # Development/feature branches: verbose debugging
        return logging.DEBUG


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for the specified module.

    The logger is configured with:
    - Appropriate log level based on git branch (INFO for main, DEBUG for others)
    - Formatted output with timestamp, level, file, line number, function name, and message
    - Stream handler for console output

    Args:
        name: Logger name (typically __name__ from the calling module)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> from dftt_timecode.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.debug("This is a debug message")
        >>> logger.info("This is an info message")
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Determine log level
    log_level = _determine_log_level()
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d-%(funcName)s()] %(message)s'
    )

    # Create and configure stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(stream_handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger


def configure_logging(level: Optional[int] = None) -> None:
    """
    Configure logging for the entire dftt_timecode package.

    This function can be called by users to manually set the log level
    for all dftt_timecode loggers.

    Args:
        level: Optional logging level (logging.DEBUG, logging.INFO, etc.).
               If None, uses automatic detection based on git branch.

    Example:
        >>> import logging
        >>> from dftt_timecode.logging_config import configure_logging
        >>> configure_logging(logging.WARNING)  # Only show warnings and above
    """
    if level is None:
        level = _determine_log_level()

    # Configure all dftt_timecode loggers
    for logger_name in logging.Logger.manager.loggerDict:
        if logger_name.startswith('dftt_timecode'):
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)
