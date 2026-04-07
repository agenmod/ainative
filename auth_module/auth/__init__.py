"""
通用用户认证模块 — 注册、登录、忘记密码、JWT 可选
可整体复制到任意 FastAPI 项目，使项目具备用户注册/登录能力。
"""
from auth.api import router

__all__ = ["router"]
