"""
Account Lockout Manager - 账户锁定管理
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
class FailedLoginAttempt:
    """失败登录尝试"""

    id: str = field(default_factory=lambda: secrets.token_urlsafe(8))
    user_id: str = ""
    username: str = ""
    ip_address: str = ""
    attempted_at: datetime = field(default_factory=datetime.now)
    locked_until: datetime = None

    def is_locked(self) -> bool:
        """检查账户是否被锁定"""
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "ip_address": self.ip_address,
            "attempted_at": self.attempted_at.isoformat(),
            "locked_until": self.locked_until.isoformat() if self.locked_until else None,
        }


class AccountLockoutManager:
    """账户锁定管理器"""

    DEFAULT_MAX_ATTEMPTS = 5
    DEFAULT_LOCKOUT_DURATION_MINUTES = 30

    def __init__(
        self,
        db_path: Path,
        max_attempts: int = None,
        lockout_duration_minutes: int = None,
    ):
        """
        初始化账户锁定管理器

        Args:
            db_path: 数据库路径
            max_attempts: 最大失败尝试次数
            lockout_duration_minutes: 锁定持续时间（分钟）
        """
        self.db_path = db_path
        self.max_attempts = max_attempts or self.DEFAULT_MAX_ATTEMPTS
        self.lockout_duration_minutes = lockout_duration_minutes or self.DEFAULT_LOCKOUT_DURATION_MINUTES
        self._lock = asyncio.Lock()

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    async def record_failed_login(
        self,
        user_id: str,
        username: str,
        ip_address: str = "",
    ) -> FailedLoginAttempt:
        """
        记录失败登录尝试

        Args:
            user_id: 用户ID
            username: 用户名
            ip_address: IP地址

        Returns:
            FailedLoginAttempt: 失败登录记录
        """
        async with self._lock:
            attempt = FailedLoginAttempt(
                user_id=user_id,
                username=username,
                ip_address=ip_address,
            )

            # 检查是否已有锁定记录
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM failed_login_attempts WHERE user_id = ? AND locked_until IS NOT NULL",
                    (user_id,),
                )
                existing = cursor.fetchone()

                if existing:
                    # 已存在锁定，更新锁定时间
                    locked_until = datetime.fromisoformat(existing[5]) if existing[5] else None
                    if locked_until and datetime.now() < locked_until:
                        # 账户仍被锁定
                        attempt.locked_until = locked_until
                        return attempt

            # 获取该用户的失败尝试次数
            cursor = conn.execute(
                "SELECT COUNT(*) FROM failed_login_attempts WHERE user_id = ? AND attempted_at > ?",
                (user_id, (datetime.now() - timedelta(minutes=self.lockout_duration_minutes)).isoformat()),
            )
            count = cursor.fetchone()[0]

            # 如果超过阈值，锁定账户
            if count + 1 >= self.max_attempts:
                attempt.locked_until = datetime.now() + timedelta(minutes=self.lockout_duration_minutes)

            conn.execute(
                """
                INSERT INTO failed_login_attempts
                (id, user_id, username, ip_address, attempted_at, locked_until)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    attempt.id,
                    attempt.user_id,
                    attempt.username,
                    attempt.ip_address,
                    attempt.attempted_at.isoformat(),
                    attempt.locked_until.isoformat() if attempt.locked_until else None,
                ),
            )
            conn.commit()

            return attempt

    async def is_account_locked(self, user_id: str) -> bool:
        """
        检查账户是否被锁定

        Args:
            user_id: 用户ID

        Returns:
            bool: 账户是否被锁定
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT locked_until FROM failed_login_attempts WHERE user_id = ? ORDER BY attempted_at DESC LIMIT 1",
                (user_id,),
            )
            row = cursor.fetchone()

        if not row or row[0] is None:
            return False

        locked_until = datetime.fromisoformat(row[0])
        return datetime.now() < locked_until

    async def get_failed_attempts(self, user_id: str) -> List[FailedLoginAttempt]:
        """获取用户的失败登录尝试记录"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM failed_login_attempts WHERE user_id = ? ORDER BY attempted_at DESC",
                (user_id,),
            )
            attempts = []
            for row in cursor.fetchall():
                attempt = FailedLoginAttempt(
                    id=row[0],
                    user_id=row[1],
                    username=row[2],
                    ip_address=row[3] or "",
                    attempted_at=datetime.fromisoformat(row[4]),
                    locked_until=datetime.fromisoformat(row[5]) if row[5] else None,
                )
                attempts.append(attempt)
            return attempts

    async def unlock_account(self, user_id: str, admin_user_id: str = None) -> bool:
        """
        解锁账户

        Args:
            user_id: 要解锁的用户ID
            admin_user_id: 管理员用户ID（执行解锁操作）

        Returns:
            bool: 是否解锁成功
        """
        async with self._lock:
            with self._get_connection() as conn:
                # 删除失败尝试记录
                conn.execute(
                    "DELETE FROM failed_login_attempts WHERE user_id = ?",
                    (user_id,),
                )
                conn.commit()

            return True

    async def reset_failed_attempts(self, user_id: str) -> int:
        """
        重置失败尝试计数（成功登录后调用）

        Args:
            user_id: 用户ID

        Returns:
            int: 被删除的记录数
        """
        async with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM failed_login_attempts WHERE user_id = ?",
                    (user_id,),
                )
                conn.commit()
                return cursor.rowcount

    async def check_login_allowed(self, user_id: str) -> tuple[bool, str]:
        """
        检查是否允许登录

        Args:
            user_id: 用户ID

        Returns:
            tuple[bool, str]: (是否允许, 错误消息)
        """
        if await self.is_account_locked(user_id):
            return False, t("errors.account_locked")

        attempts = await self.get_failed_attempts(user_id)
        recent_attempts = [
            a for a in attempts
            if datetime.now() - a.attempted_at < timedelta(minutes=self.lockout_duration_minutes)
        ]

        remaining = self.max_attempts - len(recent_attempts)
        if remaining <= 0:
            return False, t("errors.account_locked")

        if remaining <= 2:
            return True, t("errors.login_attempts_remaining", remaining=remaining)

        return True, ""