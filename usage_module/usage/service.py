"""用户级 LLM 用量：检查额度、记录用量、查询、管理"""
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from usage.config import settings
from usage.models import UserLlmUsage, UsageRecord


def _get_or_create(db: Session, user_id: UUID) -> UserLlmUsage:
    row = db.query(UserLlmUsage).filter(UserLlmUsage.user_id == user_id).first()
    if row is None:
        row = UserLlmUsage(
            user_id=user_id,
            tokens_used=0,
            tokens_limit=settings.DEFAULT_TOKEN_LIMIT,
            subscription_tier="free",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def check_quota(user_id: UUID, db: Session) -> Dict[str, Any]:
    """
    调用前检查用户额度。
    Returns: {"ok": bool, "used": int, "limit": int, "remaining": int}
    ok=False 时接入方应拒绝 LLM 调用并返回友好提示。
    """
    row = _get_or_create(db, user_id)
    limit = row.effective_limit()
    used = row.tokens_used or 0
    remaining = max(0, limit - used)
    return {
        "ok": remaining > 0,
        "used": int(used),
        "limit": int(limit),
        "remaining": int(remaining),
    }


def get_quota(user_id: UUID, db: Session) -> Dict[str, Any]:
    """供 API/前端展示：used, limit, remaining, subscription_tier"""
    row = _get_or_create(db, user_id)
    limit = row.effective_limit()
    used = row.tokens_used or 0
    remaining = max(0, limit - used)
    return {
        "used": int(used),
        "limit": int(limit),
        "remaining": int(remaining),
        "subscription_tier": (row.subscription_tier or "free"),
    }


def record_usage(
    user_id: UUID,
    tokens_used: int,
    db: Session,
    model_id: Optional[str] = None,
    cost_cent: Optional[int] = None,
) -> None:
    """
    调用成功后扣减额度。累加 tokens_used，可选写入 usage_records 明细。
    """
    if not user_id or tokens_used <= 0:
        return
    row = _get_or_create(db, user_id)
    row.tokens_used = (row.tokens_used or 0) + tokens_used
    db.commit()
    if settings.ENABLE_USAGE_RECORDS:
        rec = UsageRecord(
            user_id=user_id,
            tokens=tokens_used,
            model_id=model_id,
            cost_cent=cost_cent,
        )
        db.add(rec)
        db.commit()


def set_limit(user_id: UUID, limit: int, db: Session) -> None:
    """管理端：设置用户额度上限"""
    row = _get_or_create(db, user_id)
    row.tokens_limit = limit
    db.commit()


def reset_used(user_id: UUID, db: Session) -> None:
    """管理端：重置用户已用量为 0"""
    row = _get_or_create(db, user_id)
    row.tokens_used = 0
    db.commit()


def add_quota(user_id: UUID, tokens: int, db: Session) -> None:
    """发放额度：增加用户 tokens_limit（或可用于活动赠送）"""
    row = _get_or_create(db, user_id)
    current = row.tokens_limit if row.tokens_limit is not None else settings.DEFAULT_TOKEN_LIMIT
    row.tokens_limit = current + tokens
    db.commit()
