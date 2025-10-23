"""
Tests for logging configuration module.

Tests the automatic log level detection based on git branch and
environment variable configuration.
"""

import logging
import subprocess
from unittest.mock import patch

from dftt_timecode.logging_config import (
    _determine_log_level,
    _get_git_branch,
    configure_logging,
    get_logger,
)


class TestGitBranchDetection:
    """Test git branch detection functionality."""

    def test_get_git_branch_in_repo(self):
        """Test that _get_git_branch returns a branch name when in a git repo."""
        branch = _get_git_branch()
        # Should return a string (branch name) or None if not in repo
        assert branch is None or isinstance(branch, str)

    @patch('subprocess.run')
    def test_get_git_branch_success(self, mock_run):
        """Test successful git branch detection."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = 'main\n'

        branch = _get_git_branch()
        assert branch == 'main'

    @patch('subprocess.run')
    def test_get_git_branch_not_in_repo(self, mock_run):
        """Test behavior when not in a git repository."""
        mock_run.return_value.returncode = 128
        mock_run.return_value.stdout = ''

        branch = _get_git_branch()
        assert branch is None

    @patch('subprocess.run')
    def test_get_git_branch_timeout(self, mock_run):
        """Test behavior when git command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired('git', 2)

        branch = _get_git_branch()
        assert branch is None

    @patch('subprocess.run')
    def test_get_git_branch_file_not_found(self, mock_run):
        """Test behavior when git is not installed."""
        mock_run.side_effect = FileNotFoundError()

        branch = _get_git_branch()
        assert branch is None


class TestLogLevelDetermination:
    """Test log level determination logic."""

    def test_determine_log_level_with_env_debug(self, monkeypatch):
        """Test that DFTT_LOG_LEVEL env var sets DEBUG level."""
        monkeypatch.setenv('DFTT_LOG_LEVEL', 'DEBUG')
        level = _determine_log_level()
        assert level == logging.DEBUG

    def test_determine_log_level_with_env_info(self, monkeypatch):
        """Test that DFTT_LOG_LEVEL env var sets INFO level."""
        monkeypatch.setenv('DFTT_LOG_LEVEL', 'INFO')
        level = _determine_log_level()
        assert level == logging.INFO

    def test_determine_log_level_with_env_warning(self, monkeypatch):
        """Test that DFTT_LOG_LEVEL env var sets WARNING level."""
        monkeypatch.setenv('DFTT_LOG_LEVEL', 'WARNING')
        level = _determine_log_level()
        assert level == logging.WARNING

    def test_determine_log_level_with_env_error(self, monkeypatch):
        """Test that DFTT_LOG_LEVEL env var sets ERROR level."""
        monkeypatch.setenv('DFTT_LOG_LEVEL', 'ERROR')
        level = _determine_log_level()
        assert level == logging.ERROR

    def test_determine_log_level_with_env_critical(self, monkeypatch):
        """Test that DFTT_LOG_LEVEL env var sets CRITICAL level."""
        monkeypatch.setenv('DFTT_LOG_LEVEL', 'CRITICAL')
        level = _determine_log_level()
        assert level == logging.CRITICAL

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_determine_log_level_with_invalid_env(self, mock_get_branch, monkeypatch):
        """Test that invalid DFTT_LOG_LEVEL env var is ignored."""
        monkeypatch.setenv('DFTT_LOG_LEVEL', 'INVALID')
        # Mock git to return a dev branch for predictable testing
        mock_get_branch.return_value = 'dev'
        level = _determine_log_level()
        # Should fall back to branch-based detection
        assert level == logging.DEBUG

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_determine_log_level_main_branch(self, mock_get_branch, monkeypatch):
        """Test that main branch gets INFO level."""
        monkeypatch.delenv('DFTT_LOG_LEVEL', raising=False)
        mock_get_branch.return_value = 'main'

        level = _determine_log_level()
        assert level == logging.INFO

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_determine_log_level_dev_branch(self, mock_get_branch, monkeypatch):
        """Test that dev branch gets DEBUG level."""
        monkeypatch.delenv('DFTT_LOG_LEVEL', raising=False)
        mock_get_branch.return_value = 'dev'

        level = _determine_log_level()
        assert level == logging.DEBUG

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_determine_log_level_feature_branch(self, mock_get_branch, monkeypatch):
        """Test that feature branches get DEBUG level."""
        monkeypatch.delenv('DFTT_LOG_LEVEL', raising=False)
        mock_get_branch.return_value = 'feature/new-feature'

        level = _determine_log_level()
        assert level == logging.DEBUG

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_determine_log_level_no_git(self, mock_get_branch, monkeypatch):
        """Test that INFO is used when git info unavailable (built packages)."""
        monkeypatch.delenv('DFTT_LOG_LEVEL', raising=False)
        mock_get_branch.return_value = None

        level = _determine_log_level()
        assert level == logging.INFO

    def test_env_var_overrides_branch(self, monkeypatch):
        """Test that environment variable takes priority over branch detection."""
        monkeypatch.setenv('DFTT_LOG_LEVEL', 'ERROR')
        # Even if we're on main branch, env var should win
        level = _determine_log_level()
        assert level == logging.ERROR

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_installed_package_defaults_to_info(self, mock_get_branch, monkeypatch):
        """Test that installed packages (no git) default to INFO level."""
        monkeypatch.delenv('DFTT_LOG_LEVEL', raising=False)
        mock_get_branch.return_value = None

        level = _determine_log_level()
        # Built/installed packages should use INFO, not DEBUG
        assert level == logging.INFO


class TestGetLogger:
    """Test logger creation and configuration."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger('test_module')
        assert isinstance(logger, logging.Logger)

    def test_get_logger_has_handler(self):
        """Test that logger has at least one handler configured."""
        logger = get_logger('test_module_2')
        assert len(logger.handlers) > 0

    def test_get_logger_has_formatter(self):
        """Test that logger's handler has a formatter configured."""
        logger = get_logger('test_module_3')
        handler = logger.handlers[0]
        assert handler.formatter is not None

    def test_get_logger_no_propagate(self):
        """Test that logger doesn't propagate to root logger."""
        logger = get_logger('test_module_4')
        assert logger.propagate is False

    def test_get_logger_idempotent(self):
        """Test that calling get_logger multiple times doesn't add duplicate handlers."""
        logger1 = get_logger('test_module_5')
        handler_count_1 = len(logger1.handlers)

        logger2 = get_logger('test_module_5')
        handler_count_2 = len(logger2.handlers)

        assert logger1 is logger2
        assert handler_count_1 == handler_count_2

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_get_logger_level_main_branch(self, mock_get_branch, monkeypatch):
        """Test that logger has INFO level on main branch."""
        monkeypatch.delenv('DFTT_LOG_LEVEL', raising=False)
        mock_get_branch.return_value = 'main'

        logger = get_logger('test_module_main')
        assert logger.level == logging.INFO

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_get_logger_level_dev_branch(self, mock_get_branch, monkeypatch):
        """Test that logger has DEBUG level on dev branch."""
        monkeypatch.delenv('DFTT_LOG_LEVEL', raising=False)
        mock_get_branch.return_value = 'dev'

        logger = get_logger('test_module_dev')
        assert logger.level == logging.DEBUG


class TestConfigureLogging:
    """Test manual logging configuration."""

    def test_configure_logging_with_level(self):
        """Test that configure_logging sets specified level."""
        # Create a test logger first
        logger = get_logger('dftt_timecode.test_config')

        # Configure to WARNING
        configure_logging(logging.WARNING)

        # Check that the level was updated
        assert logger.level == logging.WARNING

    @patch('dftt_timecode.logging_config._get_git_branch')
    def test_configure_logging_without_level(self, mock_get_branch):
        """Test that configure_logging uses automatic detection when level not specified."""
        # Create a test logger first
        logger = get_logger('dftt_timecode.test_config_2')

        # Mock git to return main branch
        mock_get_branch.return_value = 'main'

        # Configure without specifying level
        configure_logging()

        # Should use branch-based detection (INFO for main)
        assert logger.level == logging.INFO

    def test_configure_logging_updates_handlers(self):
        """Test that configure_logging updates handler levels."""
        # Create a test logger first
        logger = get_logger('dftt_timecode.test_config_3')

        # Configure to ERROR
        configure_logging(logging.ERROR)

        # Check that handlers were updated
        for handler in logger.handlers:
            assert handler.level == logging.ERROR


class TestIntegration:
    """Integration tests for logging system."""

    def test_dftt_timecode_uses_logging_config(self):
        """Test that DfttTimecode module uses the new logging config."""
        from dftt_timecode.core.dftt_timecode import logger

        # Should be a proper Logger instance
        assert isinstance(logger, logging.Logger)

        # Should have handlers configured
        assert len(logger.handlers) > 0

    def test_logging_exports_from_main_package(self):
        """Test that logging functions are exported from main package."""
        from dftt_timecode import configure_logging as conf
        from dftt_timecode import get_logger as gl

        assert callable(conf)
        assert callable(gl)

    def test_real_world_usage(self):
        """Test a real-world usage scenario."""
        # Import and create a timecode
        from dftt_timecode import DfttTimecode

        # This should not raise any errors
        tc = DfttTimecode('01:00:00:00', fps=24)
        assert tc is not None
