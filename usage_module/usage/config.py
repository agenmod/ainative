"""用量模块配置 — 默认额度、表名等，可通过环境变量覆盖"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class UsageSettings(BaseSettings):
    """用户级 LLM 用量 / 限免额度相关配置"""

    # 数据库（模块自带 user_llm_usage 表时必填；与接入方同库则填同一连接串）
    DATABASE_URL: str = ""

    # 默认每用户 token 额度（限免）
    DEFAULT_TOKEN_LIMIT: int = 500_000

    # 本模块表名（若接入方已有 users 表上的 used/limit 字段，可不建 user_llm_usage）
    TABLE_USER_LLM_USAGE: str = "user_llm_usage"
    TABLE_USAGE_RECORDS: str = "usage_records"

    # 接入方 User 表上字段名（方案 A：不建 user_llm_usage，直接用 User 表列）
    # 留空表示使用本模块自带的 user_llm_usage 表
    USER_TABLE_TOKENS_USED_COLUMN: str = ""
    USER_TABLE_TOKENS_LIMIT_COLUMN: str = ""

    # 是否在 record_usage 时写入用量明细表（便于计费/对账）
    ENABLE_USAGE_RECORDS: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "USAGE_"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_usage_settings() -> UsageSettings:
    return UsageSettings()


settings = get_usage_settings()
