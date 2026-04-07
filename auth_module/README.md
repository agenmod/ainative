# 通用用户认证模块

提供**用户注册、登录、忘记密码、重置密码**的完整后端实现，可整体复制到任意 FastAPI 项目，使项目具备“用户可注册、可登录、有用户记录”的能力。

## 功能

- 注册：用户名/邮箱唯一、bcrypt 密码哈希、可选头像生成
- 登录：限流、登录失败锁定、可选 JWT 签发
- 忘记密码 / 重置密码：Redis 存 token、可选 SMTP 发邮件
- 可选 JWT 模式：配置 `JWT_SECRET` 后登录返回 `access_token`，受保护路由使用 `Depends(get_current_user)`

## 依赖

- Python 3.10+
- PostgreSQL（必选）
- Redis（可选；未配置时限流/重置密码不可用或降级）

安装：`pip install -r requirements.txt`

配置模板（占位值，可复制为 `.env`）：[`env.example`](env.example)。最小运行示例：[`examples/minimal_app.py`](examples/minimal_app.py)。

## 配置（环境变量）

| 变量 | 必选 | 说明 |
|------|------|------|
| DATABASE_URL | 是 | PostgreSQL 连接串 |
| REDIS_URL | 否 | Redis 连接串；空则不限流、不存重置 token |
| JWT_SECRET | 否 | 配置后登录返回 token，并支持 GET /me、get_current_user |
| SMTP_HOST, SMTP_USER, SMTP_PASSWORD | 否 | 忘记密码发邮件 |
| SITE_URL | 否 | 重置链接前缀，如 `https://example.com` |

## 快速跑通

1. 创建数据库并执行 `migrations_or_sql/user_table.sql`。
2. 设置 `DATABASE_URL`（及可选的 `REDIS_URL`、`JWT_SECRET`）。
3. 在 FastAPI 应用中挂载路由：

```python
from auth.api import router as auth_router
app.include_router(auth_router, prefix="/api/v1/users", tags=["auth"])
```

4. 前端调用 `POST /api/v1/users/register`、`POST /api/v1/users/login` 等。

详细接入步骤、双模式说明（简单模式 vs JWT 模式）见 **AUTH_INTEGRATION.md**。

## 与宿主项目的关系

本目录为**独立交付物**：可复制到任意 FastAPI 仓库，按 AUTH_INTEGRATION.md 挂载路由与数据库。是否与宿主项目已有用户系统并存，由接入方自行决定。
