"""密码哈希与 JWT"""
from datetime import datetime, timezone, timedelta
from typing import Optional

from auth.models import User
from auth.config import settings


def hash_password(password: str) -> str:
    return User.hash_password(password)


def verify_password(user: User, password: str) -> bool:
    return user.verify_password(password)


def create_access_token(sub: str, expires_delta_minutes: Optional[int] = None) -> str:
    """签发 JWT，sub 建议为 str(user.id)"""
    try:
        from jose import jwt
    except ImportError:
        raise RuntimeError("JWT 需要安装: pip install python-jose[cryptography]")
    if not settings.JWT_SECRET:
        raise RuntimeError("未配置 JWT_SECRET，无法签发 token")
    expire_min = expires_delta_minutes or settings.JWT_EXPIRE_MINUTES
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expire_min),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[str]:
    """解析 JWT 返回 sub（通常为 user_id），无效则返回 None"""
    try:
        from jose import jwt
    except ImportError:
        return None
    if not settings.JWT_SECRET:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload.get("sub")
    except Exception:
        return None
