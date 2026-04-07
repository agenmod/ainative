"""依赖项：get_db、get_current_user_id（接入方可通过 dependency_overrides 注入自己的实现）"""
from uuid import UUID
from typing import Generator

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from usage.database import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话。默认使用本模块 database 的 SessionLocal（需配置 USAGE_DATABASE_URL）。
    接入方若使用同一数据库，设置 USAGE_DATABASE_URL 为相同连接串即可；
    也可通过 app.dependency_overrides[usage.deps.get_db] = your_get_db 替换。
    """
    yield from _get_db()


def get_current_user_id() -> UUID:
    """
    返回当前登录用户 ID，用于 GET /me/quota。
    默认抛出 401；接入方必须通过 app.dependency_overrides[get_current_user_id] = your_get_user_id
    注入自己的鉴权（如从 JWT、session 解析出 user_id）。
    """
    raise HTTPException(
        status_code=401,
        detail="Authentication required. Override usage.deps.get_current_user_id with your auth (e.g. JWT or session).",
    )
