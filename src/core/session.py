"""
Session Management Module

Provides session state management for login and UI state.
Replaces scattered state in events.py with centralized management.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages login session state and last input state.

    Provides thread-safe access to:
    - Login browser state (playwright context, page, process)
    - Last user input (template, content)
    """

    _instance: Optional["SessionManager"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "SessionManager":
        """Singleton pattern for global session state."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Login state
        self._login_state: Dict[str, Any] = {"p": None, "context": None, "page": None}
        self._login_lock: Optional[asyncio.Lock] = None

        # Last input state
        self._last_input: Dict[str, str] = {"template": "摘要总结", "content": ""}
        self._last_input_lock: Optional[asyncio.Lock] = None

        self._initialized = True

    # Login state management

    @property
    def login_state(self) -> Dict[str, Any]:
        """Get the current login state."""
        return self._login_state

    def get_login_lock(self) -> asyncio.Lock:
        """Get or create the login lock."""
        if self._login_lock is None:
            self._login_lock = asyncio.Lock()
        return self._login_lock

    def update_login_state(self, **kwargs: Any) -> None:
        """Update login state fields."""
        self._login_state.update(kwargs)

    def clear_login_state(self) -> None:
        """Clear login state."""
        self._login_state = {"p": None, "context": None, "page": None}

    # Last input management

    @property
    def last_input(self) -> Dict[str, str]:
        """Get the last input state."""
        return self._last_input

    def get_last_input_lock(self) -> asyncio.Lock:
        """Get or create the last input lock."""
        if self._last_input_lock is None:
            self._last_input_lock = asyncio.Lock()
        return self._last_input_lock

    def update_last_input(self, template: str, content: str) -> None:
        """Update last input state."""
        self._last_input["template"] = template
        self._last_input["content"] = content


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Convenience functions for backward compatibility with events.py


def get_login_lock():
    """Get the login lock for browser operations."""
    return get_session_manager().get_login_lock()


def get_last_input_lock():
    """Get the last input lock for thread-safe access."""
    return get_session_manager().get_last_input_lock()


LOGIN_STATE: Dict[str, Any] = get_session_manager().login_state
LAST_INPUT: Dict[str, str] = get_session_manager().last_input
