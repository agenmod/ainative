"""
用户级大模型用量 / 限免额度 / 计费 — 通用模块

提供：check_quota、record_usage、get_quota、set_limit、reset_used、add_quota
接入方在 LLM 调用前调用 check_quota，调用成功后调用 record_usage。
"""
from usage.service import check_quota, record_usage, get_quota, set_limit, reset_used, add_quota
from usage.api import router

__all__ = [
    "check_quota",
    "record_usage",
    "get_quota",
    "set_limit",
    "reset_used",
    "add_quota",
    "router",
]
