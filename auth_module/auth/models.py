"""用户模型 — 仅认证与基础资料字段，无业务表关联"""
import hashlib
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from auth.database import Base


class User(Base):
    """用户表（通用认证用）"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 可选资料
    gender = Column(String(20))  # male / female / other
    bio = Column(Text)
    age = Column(Integer)
    occupation = Column(String(100))
    hometown = Column(String(100))
    current_city = Column(String(100))
    interests = Column(Text, default="[]")  # JSON 数组字符串

    @staticmethod
    def hash_password(password: str) -> str:
        import bcrypt
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        import bcrypt
        stored = self.password_hash or ""
        if stored.startswith("$2b$") or stored.startswith("$2a$"):
            try:
                return bcrypt.checkpw(
                    password.encode("utf-8"),
                    stored.encode("utf-8"),
                )
            except Exception:
                return False
        if len(stored) == 64:
            if stored == hashlib.sha256(password.encode()).hexdigest():
                self.password_hash = self.hash_password(password)
                return True
        return False
