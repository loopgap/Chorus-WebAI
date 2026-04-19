"""
Session Manager - 认证会话生命周期管理
"""

from __future__ import annotations

import asyncio
import secrets
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from src.utils.i18n import t


@dataclass
class AuthSession:
    """认证会话"""

    id: str = field(default_factory=lambda: secrets.token_urlsafe(16))
    user_id: str = ""
    username: str = ""
    ip_address: str = ""
    user_agent: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    active: bool = True

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return datetime.now() > self.expires_at or not self.active

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "active": self.active,
        }


class SessionManager:
    """会话管理器 - 管理认证会话生命周期"""

    def __init__(self, db_path: Path, secret_key: str = None):
        """
        初始化会话管理器

        Args:
            db_path: 数据库路径
            secret_key: JWT密钥（用于会话令牌）
        """
        import os

        self.db_path = db_path
        self.secret_key = secret_key or os.getenv("SHADOW_JWT_SECRET")
        self._lock = asyncio.Lock()

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    async def create_session(
        self,
        user_id: str,
        username: str,
        ip_address: str = "",
        user_agent: str = "",
        expiry_hours: int = 24,
    ) -> AuthSession:
        """
        创建新会话

        Args:
            user_id: 用户ID
            username: 用户名
            ip_address: IP地址
            user_agent: 用户代理
            expiry_hours: 过期时间（小时）

        Returns:
            AuthSession: 新创建的会话
        """
        async with self._lock:
            session = AuthSession(
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.now() + timedelta(hours=expiry_hours),
            )

            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO auth_sessions
                    (id, user_id, username, ip_address, user_agent, created_at, last_activity, expires_at, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session.id,
                        session.user_id,
                        session.username,
                        session.ip_address,
                        session.user_agent,
                        session.created_at.isoformat(),
                        session.last_activity.isoformat(),
                        session.expires_at.isoformat(),
                        1 if session.active else 0,
                    ),
                )
                conn.commit()

            return session

    async def get_session(self, session_id: str) -> AuthSession:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            AuthSession: 会话对象

        Raises:
            ValueError: 会话不存在或已过期
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM auth_sessions WHERE id = ?",
                (session_id,),
            )
            row = cursor.fetchone()

        if not row:
            raise ValueError(t("errors.session_not_found"))

        session = AuthSession(
            id=row[0],
            user_id=row[1],
            username=row[2],
            ip_address=row[3] or "",
            user_agent=row[4] or "",
            created_at=datetime.fromisoformat(row[5]),
            last_activity=datetime.fromisoformat(row[6]),
            expires_at=datetime.fromisoformat(row[7]),
            active=bool(row[8]),
        )

        if session.is_expired():
            raise ValueError(t("errors.session_expired"))

        return session

    async def validate_session(self, session_id: str) -> bool:
        """
        验证会话是否有效

        Args:
            session_id: 会话ID

        Returns:
            bool: 会话是否有效
        """
        try:
            session = await self.get_session(session_id)
            return session.active and not session.is_expired()
        except ValueError:
            return False

    async def update_activity(self, session_id: str) -> None:
        """更新会话最后活动时间"""
        async with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE auth_sessions SET last_activity = ? WHERE id = ?",
                    (datetime.now().isoformat(), session_id),
                )
                conn.commit()

    async def expire_session(self, session_id: str) -> None:
        """使会话过期"""
        async with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE auth_sessions SET active = 0 WHERE id = ?",
                    (session_id,),
                )
                conn.commit()

    async def expire_all_user_sessions(self, user_id: str) -> int:
        """
        使指定用户的所有会话过期

        Args:
            user_id: 用户ID

        Returns:
            int: 被过期的会话数量
        """
        async with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE auth_sessions SET active = 0 WHERE user_id = ? AND active = 1",
                    (user_id,),
                )
                conn.commit()
                return cursor.rowcount

    async def get_user_sessions(self, user_id: str) -> List[AuthSession]:
        """获取用户的所有活跃会话"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM auth_sessions WHERE user_id = ? AND active = 1 ORDER BY created_at DESC",
                (user_id,),
            )
            sessions = []
            for row in cursor.fetchall():
                session = AuthSession(
                    id=row[0],
                    user_id=row[1],
                    username=row[2],
                    ip_address=row[3] or "",
                    user_agent=row[4] or "",
                    created_at=datetime.fromisoformat(row[5]),
                    last_activity=datetime.fromisoformat(row[6]),
                    expires_at=datetime.fromisoformat(row[7]),
                    active=bool(row[8]),
                )
                if not session.is_expired():
                    sessions.append(session)
            return sessions

    async def cleanup_expired_sessions(self) -> int:
        """
        清理所有过期的会话

        Returns:
            int: 被清理的会话数量
        """
        async with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE auth_sessions SET active = 0 WHERE active = 1 AND expires_at < ?",
                    (datetime.now().isoformat(),),
                )
                conn.commit()
                return cursor.rowcount