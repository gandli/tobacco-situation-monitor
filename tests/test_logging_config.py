"""Test logging configuration."""

import logging
from unittest.mock import patch

import pytest

from tsm.logging_config import setup_logging


def test_setup_logging():
    """Test that logging is configured correctly."""
    # Capture the root logger before setup
    root_logger = logging.getLogger()
    original_level = root_logger.level
    
    # Setup logging
    setup_logging(debug=True)
    
    # Verify log level is set to DEBUG when debug=True
    assert root_logger.level == logging.DEBUG
    
    # Reset to original level
    root_logger.setLevel(original_level)


def test_setup_logging_production():
    """Test that logging is configured for production."""
    root_logger = logging.getLogger()
    original_level = root_logger.level
    
    # Setup logging for production (debug=False)
    setup_logging(debug=False)
    
    # Verify log level is set to INFO when debug=False
    assert root_logger.level == logging.INFO
    
    # Reset to original level
    root_logger.setLevel(original_level)