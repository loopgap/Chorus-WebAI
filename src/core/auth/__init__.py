"""
Authentication Module

Enterprise-grade authentication and authorization
"""

from .auth_manager import (
    AuthManager,
    RBACManager,
    Role,
    Permission,
    User,
    AuditEvent,
    AuthSession,
    PasswordResetToken,
    FailedLoginAttempt,
    SessionManager,
    PasswordResetManager,
    AccountLockoutManager,
    ROLE_PERMISSIONS,
)

__all__ = [
    "AuthManager",
    "RBACManager",
    "Role",
    "Permission",
    "User",
    "AuditEvent",
    "AuthSession",
    "PasswordResetToken",
    "FailedLoginAttempt",
    "SessionManager",
    "PasswordResetManager",
    "AccountLockoutManager",
    "ROLE_PERMISSIONS",
]

# Global singleton
_auth_manager = None


def get_auth_manager() -> AuthManager:
    """Get or create the global AuthManager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager(db_path=AuthManager._default_db_path)
    return _auth_manager
