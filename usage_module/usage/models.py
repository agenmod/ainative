"""用量相关表：每用户额度聚合 + 可选用量明细（计费/对账）"""
import uuid
from sqlalchemy import Column, String, Integer, BigInteger, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from usage.database import Base
from usage.config import settings


class UserLlmUsage(Base):
    """每用户 LLM 用量与额度（聚合）"""
    __tablename__ = settings.TABLE_USER_LLM_USAGE

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    tokens_used = Column(BigInteger, default=0)
    tokens_limit = Column(BigInteger, default=None)  # None 表示用配置默认
    subscription_tier = Column(String(20), default="free")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def effective_limit(self) -> int:
        if self.tokens_limit is not None:
            return int(self.tokens_limit)
        return settings.DEFAULT_TOKEN_LIMIT


class UsageRecord(Base):
    """用量明细（可选，用于计费/对账）"""
    __tablename__ = settings.TABLE_USAGE_RECORDS

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tokens = Column(Integer, nullable=False)
    model_id = Column(String(100))
    cost_cent = Column(Integer)  # 可选：费用（分）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
