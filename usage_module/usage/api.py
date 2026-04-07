"""用量 API：当前用户额度、按 user_id 查询、可选管理端"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from usage.deps import get_db, get_current_user_id
from usage.service import get_quota, set_limit, reset_used
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/me/quota")
def get_my_quota(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """返回当前登录用户的额度信息（used, limit, remaining, subscription_tier）。需接入方注入 get_current_user_id。"""
    return get_quota(user_id, db)


@router.get("/users/{user_id}/quota")
def get_user_quota(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """按 user_id 查询额度（如前端从 localStorage 传 user_id 时使用）。接入方可按需加鉴权确保仅查本人。"""
    return get_quota(user_id, db)


# ---------- 可选：管理端（按需加 admin 鉴权） ----------

@router.patch("/admin/usage/users/{user_id}/limit")
def admin_set_user_limit(
    user_id: UUID,
    limit: int = Query(..., ge=0),
    db: Session = Depends(get_db),
):
    """管理端：设置用户额度上限。建议在接入方用 require_admin 等依赖保护此路由。"""
    if limit < 0:
        raise HTTPException(400, "limit must be >= 0")
    set_limit(user_id, limit, db)
    return {"ok": True, "user_id": str(user_id), "limit": limit}


@router.post("/admin/usage/users/{user_id}/reset-used")
def admin_reset_user_used(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """管理端：重置用户已用量为 0。建议在接入方用 require_admin 等依赖保护此路由。"""
    reset_used(user_id, db)
    return {"ok": True, "user_id": str(user_id), "message": "已重置用量"}
