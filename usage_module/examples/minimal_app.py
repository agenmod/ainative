"""
最小可运行示例：挂载用量路由。

使用前：
1. 在 usage_module 目录下执行 cp env.example .env，并设置 USAGE_DATABASE_URL
2. 执行 migrations_or_sql/usage_tables.sql，或依赖下方 startup 的 init_db()
3. pip install -r requirements.txt && pip install uvicorn

运行（在 usage_module 目录下）：
  uvicorn examples.minimal_app:app --reload

GET /me/quota 使用演示用固定 user_id；生产环境请用 dependency_overrides 注入真实鉴权。
"""
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI

from usage.api import router as usage_router
from usage.database import init_db
from usage.deps import get_current_user_id


DEMO_USER_ID = UUID("00000000-0000-4000-8000-000000000001")


def demo_get_current_user_id() -> UUID:
    """演示用：固定用户。接入方请替换为 JWT/session 解析。"""
    return DEMO_USER_ID


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="usage_module demo",
    description="Minimal FastAPI app with usage_module routes only.",
    lifespan=lifespan,
)
app.include_router(usage_router, prefix="/api/v1", tags=["usage"])
app.dependency_overrides[get_current_user_id] = demo_get_current_user_id


@app.get("/health")
def health():
    return {"status": "ok", "app": "usage_module_examples", "demo_user_id": str(DEMO_USER_ID)}
