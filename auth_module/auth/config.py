"""认证模块配置 — 从环境变量读取，便于接入方覆盖"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class AuthSettings(BaseSettings):
    """认证相关配置，所有字段均可通过环境变量覆盖"""

    # 数据库（必选）
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/mydb"

    # Redis（可选；未配置时限流/重置密码降级为不启用或内存）
    REDIS_URL: str = ""

    # JWT（可选；配置后登录可返回 access_token，并支持 get_current_user）
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 默认 24 小时

    # 邮件（可选；忘记密码发重置链接）
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "系统"
    SMTP_USE_TLS: bool = True

    # 站点地址（重置链接域名）
    SITE_URL: str = "http://localhost"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


settings = get_auth_settings()
