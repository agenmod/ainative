# 通用认证模块接入指南（给接入方 / 其他 AI）

本文档说明如何将本认证模块接入**任意 FastAPI 项目**，使项目具备：用户可注册、可登录、有用户记录、可选忘记密码与重置、可选 JWT 鉴权。

---

## 1. 概述

本模块提供：

- **注册**：`POST /users/register`
- **登录**：`POST /users/login`（可选返回 JWT）
- **获取用户**：`GET /users/{user_id}`、可选 `GET /users/me`（需 JWT）
- **忘记密码**：`POST /users/forgot-password`
- **重置密码**：`POST /users/reset-password`、`GET /users/check-reset-token/{token}`

接入后，你的项目即拥有“用户表 + 注册/登录/重置”能力；需要登录才能访问的接口可选用**简单模式**（前端传 `user_id`）或 **JWT 模式**（请求头带 `Authorization: Bearer <token>`，服务端校验）。

---

## 2. 前置条件

- Python 3.10+
- 已有或可新建 **PostgreSQL** 数据库
- **Redis** 可选；未配置时：限流与登录锁定不生效，忘记密码/重置密码依赖 Redis 存 token，将返回 503

---

## 3. 步骤 1：复制模块与依赖

- 将本 **auth_module** 目录整体复制到你的项目下（例如项目根目录下的 `auth_module/`）。
- 安装依赖：  
  `pip install -r auth_module/requirements.txt`  
  若你的项目已有 FastAPI/SQLAlchemy 等，可只补充缺失的包（如 `bcrypt`、`redis`、`python-jose[cryptography]`）。

---

## 4. 步骤 2：配置

在项目环境（`.env` 或系统环境变量）中配置以下变量：

| 变量 | 必选 | 说明 |
|------|------|------|
| DATABASE_URL | 是 | PostgreSQL 连接串，如 `postgresql://user:pass@localhost:5432/mydb` |
| REDIS_URL | 否 | Redis 连接串，如 `redis://localhost:6379/0`。不配置则不限流、不存重置 token |
| JWT_SECRET | 否 | 密钥字符串。配置后登录返回 `access_token`，并支持 `GET /me`、`get_current_user` |
| JWT_EXPIRE_MINUTES | 否 | Token 有效期（分钟），默认 1440（24 小时） |
| SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_NAME, SMTP_USE_TLS | 否 | 忘记密码发邮件用 |
| SITE_URL | 否 | 站点地址，用于重置链接，如 `https://yourdomain.com` |

模块通过 `auth.config` 的 `AuthSettings` 读取上述变量（pydantic-settings，自动从 `.env` 加载）。若你希望复用项目已有配置，可修改 `auth/config.py` 从你的 settings 导入，或通过环境变量覆盖。

---

## 5. 步骤 3：数据库

创建 User 表，与 `auth/models.User` 一致。

- **方式 A**：执行 `auth_module/migrations_or_sql/user_table.sql`（PostgreSQL）。
- **方式 B**：在接入方使用 Alembic 等迁移工具，表结构参考该 SQL 或 `auth/models.py`。

若你已有 User 表，需保证字段兼容（至少包含：id, username, email, password_hash, nickname, avatar_url, is_active, is_admin, created_at，及可选的 gender, bio, age, occupation, hometown, current_city, interests）。否则可新建一张表并只给本模块使用。

---

## 6. 步骤 4：挂载路由

在你的 FastAPI 应用中挂载认证路由，并确保能解析 `auth` 包（将 `auth_module` 所在目录加入 `sys.path`，或把 `auth` 包放到已存在路径下）：

```python
# 若 auth_module 在项目根下，且项目根在 PYTHONPATH 中，且 auth_module 下有 auth 包：
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "auth_module"))

from auth.api import router as auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/api/v1/users", tags=["auth"])
```

请根据你的项目结构调整 `sys.path` 或包位置，使 `from auth.api import router` 可执行。CORS 如需要请自行在 app 上配置。

---

## 7. 步骤 5：前端

### 请求格式

- **注册**：`POST /api/v1/users/register`  
  Body: `{ "username", "email", "password", "gender?", "nickname?", "avatar_url?", "bio?", ... }`
- **登录**：`POST /api/v1/users/login`  
  Body: `{ "username", "password" }`  
  响应：用户信息对象；若配置了 JWT_SECRET，还会返回 `access_token`、`token_type: "bearer"`。
- **获取当前用户（JWT）**：`GET /api/v1/users/me`  
  Header: `Authorization: Bearer <access_token>`
- **忘记密码**：`POST /api/v1/users/forgot-password`  
  Body: `{ "email" }`
- **重置密码**：`POST /api/v1/users/reset-password`  
  Body: `{ "token", "new_password" }`
- **检查重置链接**：`GET /api/v1/users/check-reset-token/{token}`

### 两种使用模式

- **简单模式**：登录后只使用响应里的用户信息，前端存到 localStorage，需要“当前用户”的接口由前端在 body/query 里传 `user_id`。服务端**不校验**该 `user_id` 是否来自合法登录态，仅适合内网或低安全场景。
- **JWT 模式**：登录后前端保存 `access_token`，请求需登录的接口时在 Header 中带 `Authorization: Bearer <access_token>`。服务端在需要鉴权的路由上使用 `Depends(get_current_user)` 获取当前用户并校验（见步骤 6）。

重置密码页路由约定：建议前端支持 `#/reset-password/:token`，用户在邮件中点击链接进入该页，前端先调 `check-reset-token/{token}` 再展示设置新密码表单，提交时调 `reset-password`。

---

## 8. 步骤 6：保护需要登录的接口（可选，JWT 模式）

若你配置了 `JWT_SECRET` 并采用 JWT 模式，在需要“当前登录用户”的路由上使用依赖项 `get_current_user`：

```python
from auth.deps import get_current_user
from auth.models import User

@app.get("/my-protected-route")
def my_route(current_user: User = Depends(get_current_user)):
    return {"user_id": str(current_user.id), "username": current_user.username}
```

未带有效 Token 或 Token 过期会返回 401。

---

## 9. 步骤 7：可选功能

- **忘记密码 / 重置密码**：需 Redis（存重置 token）+ 可选 SMTP（发邮件）。未配置 Redis 时接口返回 503；未配置 SMTP 时不会发邮件，但 token 仍会写入 Redis，可用其他方式把链接给用户。
- **限流与登录锁定**：依赖 Redis；未配置 REDIS_URL 时所有限流/锁定检查放行。
- **行为评分 / 滑动验证**：本模块未实现；若有需要可在 `auth.rate_limit.protect_endpoint` 中扩展。

---

## 10. 安全与模式说明

- **简单模式**（仅前端存 user、请求带 user_id）：服务端不校验“当前请求者”是否与该 user_id 对应，任何人可伪造 user_id 访问他人数据，仅适合内网或可接受该风险的场景。
- **JWT 模式**：服务端通过 JWT 校验请求身份，推荐在公网或需要安全鉴权的项目中使用。请妥善保管 `JWT_SECRET`，并设置合理的 `JWT_EXPIRE_MINUTES`。

---

## 11. 常见问题

- **没有 Redis 能否用？** 可以。不配置 REDIS_URL 时，注册/登录仍可用；限流与登录锁定不生效；忘记密码/重置密码会返回 503，如需使用则必须配置 Redis。
- **如何自定义 User 表字段？** 可修改 `auth/models.User` 增加列，并同步数据库迁移；或接入方自建 User 表并让 `auth` 使用你的表（需保证字段兼容）。
- **如何与现有 User 表合并？** 若现有表结构与 `auth/models.User` 一致，可将本模块的 `auth.database.engine` 指向同一库，并确保表名一致（`users`）；若结构不一致，需在 auth 中改用你的 Model 或做字段映射。

---

完成以上步骤后，你的项目即具备用户注册、登录、可选忘记/重置密码与 JWT 鉴权能力。将本文档与 `auth_module` 目录一并提供给其他开发者或 AI，即可按相同步骤接入到其他项目中。
