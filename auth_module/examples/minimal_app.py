"""
最小可运行示例：挂载认证路由。

使用前：
1. 在 auth_module 目录下执行 cp env.example .env，并设置 DATABASE_URL
2. 或执行 migrations_or_sql/user_table.sql 创建表；亦可依赖下方 startup 的 init_db()
3. pip install -r requirements.txt && pip install uvicorn

运行（在 auth_module 目录下）：
  uvicorn examples.minimal_app:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth.api import router as auth_router
from auth.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 演示环境：自动建表。生产环境请使用迁移脚本。
    init_db()
    yield


app = FastAPI(
    title="auth_module demo",
    description="Minimal FastAPI app with auth_module routes only.",
    lifespan=lifespan,
)
app.include_router(auth_router, prefix="/api/v1/users", tags=["auth"])


@app.get("/health")
def health():
    return {"status": "ok", "app": "auth_module_examples"}
