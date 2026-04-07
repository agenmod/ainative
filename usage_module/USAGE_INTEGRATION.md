# 用户级大模型用量模块 — 接入说明（给接入方 / 其他 AI）

本文档说明如何将本用量模块接入**任意 FastAPI 项目**，使项目具备：每用户大模型 token 用量记录、限免额度检查与扣减、前端展示与可选管理端。

---

## 1. 概述

本模块**不包含** LLM 调用逻辑，只提供「按用户维度的额度与用量」能力。接入方需要：

- 在**真正调用 LLM 之前**：取当前计费用户 `user_id` 和 `db`，调用 `check_quota(user_id, db)`；若 `not result["ok"]` 则返回 402 或友好错误。
- 在 **LLM 返回且拿到 `total_tokens` 之后**：调用 `record_usage(user_id, total_tokens, db, model_id=...)`。

`user_id` 和 `db` 必须由接入方在调用链中传入（例如从 JWT、session、或业务上的「当前使用 AI 的拥有者」等解析）。

---

## 2. 前置条件

- Python 3.10+
- FastAPI 项目，且已有或可新建 **PostgreSQL** 数据库
- 有「当前用户」概念（登录态、JWT、或业务上的 owner_user_id）

---

## 3. 步骤 1：复制模块与依赖

- 将本 **usage_module** 目录整体复制到你的项目下（例如项目根目录 `usage_module/`）。
- 安装依赖：  
  `pip install -r usage_module/requirements.txt`  
  若项目已有 FastAPI、SQLAlchemy、pydantic-settings，可只补充缺失的包。

---

## 4. 步骤 2：配置

在项目环境（`.env` 或系统环境变量）中配置：

| 变量 | 必选 | 说明 |
|------|------|------|
| USAGE_DATABASE_URL | 是 | PostgreSQL 连接串（与接入应用共用同一数据库时填相同连接串） |
| USAGE_DEFAULT_TOKEN_LIMIT | 否 | 默认每用户 token 额度，默认 500000 |
| USAGE_ENABLE_USAGE_RECORDS | 否 | 是否写入用量明细表（计费/对账），默认 false |

---

## 5. 步骤 3：数据库

在接入方使用的 PostgreSQL 库中执行：

```bash
psql $DATABASE_URL -f usage_module/migrations_or_sql/usage_tables.sql
```

将创建表 `user_llm_usage`（每用户额度聚合）和 `usage_records`（可选用量明细）。  
若你已有 `users` 表且含 `ai_platform_tokens_used` / `ai_platform_tokens_limit` 列，可只建 `usage_records` 用于明细，额度读写在接入层对接自有 User 表（本说明以使用模块自带 `user_llm_usage` 表为准）。

---

## 6. 步骤 4：挂载路由

确保能解析 `usage` 包（将 `usage_module` 所在目录加入 `sys.path`，或把 `usage` 包放到已存在路径下），然后挂载路由：

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "usage_module"))

from usage.api import router as usage_router

app = FastAPI()
# 前缀按你项目习惯，例如 /api/v1
app.include_router(usage_router, prefix="/api/v1", tags=["usage"])
```

若使用 **GET /me/quota**（当前用户额度），需要提供「当前用户 ID」的依赖，否则该接口会返回 401。见步骤 5。

---

## 7. 步骤 5：提供当前用户 ID（用于 GET /me/quota）

若你的项目已有「当前用户」依赖（例如从 JWT 解析的 `get_current_user`），可让本模块使用它：

```python
from uuid import UUID
from fastapi import Depends
from usage import deps as usage_deps

# 假设你已有 get_current_user -> User
def get_current_user_id_from_jwt(user = Depends(your_get_current_user)) -> UUID:
    return user.id

# 覆盖本模块的依赖
app.dependency_overrides[usage_deps.get_current_user_id] = get_current_user_id_from_jwt
```

这样 `GET /api/v1/me/quota` 会自动使用当前登录用户的 ID 查询额度。  
若你只使用 `GET /api/v1/users/{user_id}/quota` 且由前端传入已登录的 `user_id`，可不覆盖 `get_current_user_id`。

---

## 8. 步骤 6：在 LLM 调用处接入 check_quota 与 record_usage

在**调用 LLM 的同一层**（或封装 LLM 调用的服务里），在真正发请求前检查额度，在拿到响应后记录用量。

### 8.1 user_id 从哪来

- **按登录用户计费**：从 JWT / session 取当前用户 ID。
- **按资源拥有者计费**：例如多租户场景下，从业务模型中的 `owner_user_id` 或配置解析出的 `user_id` 取得。
- **不扣费场景**：系统内部任务、后台脚本、或使用「自定义 API / 自带 key」时，可不传 `user_id` 或不在该分支调用 `record_usage`。

### 8.2 调用前：check_quota

```python
from usage.service import check_quota

# 在调用 LLM 之前（你已有 db session 和计费用户 user_id）
quota = check_quota(user_id, db)
if not quota["ok"]:
    raise HTTPException(
        status_code=402,
        detail=f"平台额度已用完 (已使用 {quota['used']:,}/{quota['limit']:,} tokens)，请切换自己的 API 或联系管理员",
    )
# 通过后继续你的 LLM 调用
response = your_llm_client.chat.completions.create(...)
```

### 8.3 调用后：record_usage

```python
from usage.service import record_usage

# 在 LLM 返回且拿到 total_tokens 之后
total_tokens = getattr(response.usage, "total_tokens", 0)
if total_tokens > 0:
    record_usage(user_id, total_tokens, db, model_id=model_id)
```

### 8.4 示例：封装在一个「带额度的 LLM 调用」里

```python
def call_llm_with_quota(messages, user_id: UUID, db: Session, model_id: str = None):
    from usage.service import check_quota, record_usage

    quota = check_quota(user_id, db)
    if not quota["ok"]:
        raise RuntimeError(f"额度已用完: {quota['used']}/{quota['limit']}")

    response = your_llm_client.chat.completions.create(model=model_id, messages=messages)
    total_tokens = getattr(response.usage, "total_tokens", 0)
    if total_tokens > 0:
        record_usage(user_id, total_tokens, db, model_id=model_id)
    return response
```

---

## 9. 步骤 7：前端展示额度

- **当前用户额度**：`GET /api/v1/me/quota`（需已注入 `get_current_user_id`）。  
- **按 user_id**：`GET /api/v1/users/{user_id}/quota`（如从 localStorage 取当前 user_id 再请求）。

响应示例：

```json
{
  "used": 12000,
  "limit": 500000,
  "remaining": 488000,
  "subscription_tier": "free"
}
```

前端可用 `used`/`limit` 画进度条，用 `remaining` 显示剩余字数/token 提示。示例片段见 `frontend_snippets/quota_display.md`。

---

## 10. 可选：管理端

模块提供（需接入方自行加 admin 鉴权）：

- `PATCH /api/v1/admin/usage/users/{user_id}/limit?limit=1000000` — 设置用户额度上限  
- `POST /api/v1/admin/usage/users/{user_id}/reset-used` — 重置该用户已用量为 0  

建议在这些路由上增加 `Depends(require_admin)` 或等价鉴权。
