# 用户级大模型用量 / 限免额度 — 通用模块

提供**按用户维度**的 LLM token 用量累计、限免额度检查与扣减、查询接口及可选管理端，可整体复制到任意 FastAPI 项目，使项目具备「每用户大模型用量计费 / 限免」能力。

## 功能

- **额度检查**：`check_quota(user_id, db)` — 在 LLM 调用前检查，`ok=False` 时拒绝调用
- **用量记录**：`record_usage(user_id, tokens_used, db, model_id=...)` — 调用成功后累加
- **额度查询**：`get_quota(user_id, db)` — 供前端展示 used / limit / remaining
- **管理**：`set_limit`、`reset_used`、`add_quota` — 设置上限、重置已用、发放额度
- **API**：`GET /me/quota`、`GET /users/{user_id}/quota`，可选 `PATCH/POST` 管理端
- **可选**：用量明细表 `usage_records`，便于计费与对账（配置 `ENABLE_USAGE_RECORDS=True`）

## 依赖

- Python 3.10+
- PostgreSQL（本模块表 `user_llm_usage`、可选 `usage_records`）
- FastAPI、SQLAlchemy、pydantic-settings

安装：`pip install -r requirements.txt`（若你的环境已安装 FastAPI/SQLAlchemy，可只补缺）

配置模板（占位值，可复制为 `.env`）：[`env.example`](env.example)。最小运行示例：[`examples/minimal_app.py`](examples/minimal_app.py)。

## 配置（环境变量，前缀 `USAGE_`）

| 变量 | 必选 | 说明 |
|------|------|------|
| USAGE_DATABASE_URL | 是 | PostgreSQL 连接串（与接入应用使用同一数据库时填相同连接串） |
| USAGE_DEFAULT_TOKEN_LIMIT | 否 | 默认每用户 token 额度，默认 500000 |
| USAGE_ENABLE_USAGE_RECORDS | 否 | 是否写入用量明细表，默认 false |
| USAGE_TABLE_USER_LLM_USAGE | 否 | 表名，默认 user_llm_usage |
| USAGE_TABLE_USAGE_RECORDS | 否 | 明细表名，默认 usage_records |

## 快速开始

1. 在接入方数据库中执行 `migrations_or_sql/usage_tables.sql`。
2. 设置 `USAGE_DATABASE_URL`（指向你的 PostgreSQL）。
3. 挂载路由并注入鉴权：

```python
from usage.api import router as usage_router

app.include_router(usage_router, prefix="/api/v1", tags=["usage"])

# 若使用 GET /me/quota，需注入当前用户 ID（如从 JWT 解析）
# app.dependency_overrides[usage.deps.get_current_user_id] = your_get_user_id
```

4. 在 LLM 调用前调用 `check_quota(user_id, db)`，调用成功后调用 `record_usage(user_id, total_tokens, db, model_id=...)`。

详细步骤、代码示例与前端展示见 **USAGE_INTEGRATION.md**。

## 使用方式

将 `usage_module` 目录复制到你的 FastAPI 项目，在 LLM 调用链中接入 `check_quota` / `record_usage`，详见 **USAGE_INTEGRATION.md**。
