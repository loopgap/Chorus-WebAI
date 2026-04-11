"""
Core Module

Provides essential components for the ShadowBoard engine:
- Configuration management
- Browser automation
- Exception definitions
"""

from .config import ConfigManager, get_config, set_config
from .exceptions import (
    ShadowError,
    ConfigError,
    BrowserError,
    TaskError,
    WorkflowError,
    MemoryError,
)
from .browser import BrowserManager, BrowserSession

__all__ = [
    "ConfigManager",
    "get_config",
    "set_config",
    "ShadowError",
    "ConfigError",
    "BrowserError",
    "TaskError",
    "WorkflowError",
    "MemoryError",
    "BrowserManager",
    "BrowserSession",
]
