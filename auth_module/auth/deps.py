"""依赖项：get_current_user（JWT 校验）"""
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth.database import get_db
from auth.models import User
from auth.security import decode_access_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """从 Authorization: Bearer <token> 解析 JWT，返回当前用户；未提供或无效则 401"""
    if not credentials:
        raise HTTPException(status_code=401, detail="请提供认证令牌")
    sub = decode_access_token(credentials.credentials)
    if not sub:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")
    try:
        user_id = UUID(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的令牌")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    return user
