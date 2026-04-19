"""
Password Reset Manager - 密码重置功能
"""

from __future__ import annotations

import asyncio
import logging
import secrets
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from src.utils.i18n import t


@dataclass
class PasswordResetToken:
    """密码重置令牌"""

    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    user_id: str = ""
    email: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    used: bool = False

    def is_expired(self) -> bool:
        """检查令牌是否过期"""
        return datetime.now() > self.expires_at or self.used

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "token": self.token,
            "user_id": self.user_id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "used": self.used,
        }


class PasswordResetManager:
    """密码重置管理器"""

    def __init__(self, db_path: Path):
        """
        初始化密码重置管理器

        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self._lock = asyncio.Lock()

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    async def generate_reset_token(
        self,
        user_id: str,
        email: str,
        expiry_hours: int = 1,
    ) -> PasswordResetToken:
        """
        生成密码重置令牌

        Args:
            user_id: 用户ID
            email: 邮箱地址
            expiry_hours: 过期时间（小时）

        Returns:
            PasswordResetToken: 重置令牌
        """
        async with self._lock:
            # 使该用户的所有旧令牌失效
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE password_reset_tokens SET used = 1 WHERE user_id = ? AND used = 0",
                    (user_id,),
                )
                conn.commit()

            # 创建新令牌
            token = PasswordResetToken(
                user_id=user_id,
                email=email,
                expires_at=datetime.now() + timedelta(hours=expiry_hours),
            )

            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO password_reset_tokens
                    (token, user_id, email, created_at, expires_at, used)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        token.token,
                        token.user_id,
                        token.email,
                        token.created_at.isoformat(),
                        token.expires_at.isoformat(),
                        0,
                    ),
                )
                conn.commit()

            return token

    async def verify_reset_token(self, token: str) -> PasswordResetToken:
        """
        验证密码重置令牌

        Args:
            token: 重置令牌

        Returns:
            PasswordResetToken: 令牌对象

        Raises:
            ValueError: 令牌无效或已过期
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM password_reset_tokens WHERE token = ?",
                (token,),
            )
            row = cursor.fetchone()

        if not row:
            raise ValueError(t("errors.invalid_reset_token"))

        reset_token = PasswordResetToken(
            token=row[0],
            user_id=row[1],
            email=row[2],
            created_at=datetime.fromisoformat(row[3]),
            expires_at=datetime.fromisoformat(row[4]),
            used=bool(row[5]),
        )

        if reset_token.is_expired():
            raise ValueError(t("errors.reset_token_expired"))

        return reset_token

    async def mark_token_used(self, token: str) -> None:
        """标记令牌已使用"""
        async with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE password_reset_tokens SET used = 1 WHERE token = ?",
                    (token,),
                )
                conn.commit()

    async def send_reset_email(self, token: PasswordResetToken) -> bool:
        """
        发送密码重置邮件（模拟实现）

        Args:
            token: 重置令牌

        Returns:
            bool: 是否发送成功
        """
        # 实际实现中，这里会发送真实的邮件
        # 目前只是记录日志（不记录令牌内容以保证安全）
        logging.info(f"[Password Reset] Sending email to {token.email}")
        return True

    async def reset_password(self, token: str, new_password: str, auth_manager) -> bool:
        """
        使用令牌重置密码

        Args:
            token: 重置令牌
            new_password: 新密码
            auth_manager: AuthManager实例

        Returns:
            bool: 是否重置成功

        Raises:
            ValueError: 令牌无效或已过期
        """
        reset_token = await self.verify_reset_token(token)

        if reset_token.is_expired():
            raise ValueError(t("errors.reset_token_expired"))

        # 更新密码
        password_hash = auth_manager.hash_password(new_password)
        now = datetime.now()

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (password_hash, now.isoformat(), reset_token.user_id),
            )
            conn.commit()

        # 标记令牌已使用
        await self.mark_token_used(token)

        return True