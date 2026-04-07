# 可复用模块清单

本仓库提供可单独复制到任意 FastAPI 项目的**并行摘录包**。各目录自成体系：依赖说明、SQL 迁移、[`env.example`](../auth_module/env.example)（占位值）与接入文档。

## 本仓库的定位

- **agenmod** 只承载可复用模块；**不包含**完整业务应用骨架。
- 接入方将子目录复制到自己的项目后，按各模块 `README` / `*_INTEGRATION.md` 配置环境变量并挂载路由。

## 模块总览

| 模块 | 目录 | 状态 | 适用场景 | 接入文档 |
|------|------|------|----------|----------|
| 用户认证 | [auth_module/](../auth_module/) | 可用 | 注册、登录、忘记/重置密码、可选 JWT | [README](../auth_module/README.md)、[AUTH_INTEGRATION](../auth_module/AUTH_INTEGRATION.md) |
| LLM 用量 / 额度 | [usage_module/](../usage_module/) | 可用 | 按用户 token 限额、扣减、`check_quota` / `record_usage` | [README](../usage_module/README.md)、[USAGE_INTEGRATION](../usage_module/USAGE_INTEGRATION.md) |

## 依赖与配置约定

- 每个模块根目录提供 **`env.example`**（全部为占位值，可安全提交版本库）。
- 配置通过环境变量与 `pydantic-settings`，见各模块 `README`。
- 保密约定见 [SECRET_POLICY.md](SECRET_POLICY.md)。

## 最小可运行示例

各模块提供 `examples/minimal_app.py`（需本地 PostgreSQL 并执行对应 SQL）：

```bash
cd auth_module && pip install -r requirements.txt && pip install uvicorn
cp env.example .env
uvicorn examples.minimal_app:app --reload
```

```bash
cd usage_module && pip install -r requirements.txt && pip install uvicorn
cp env.example .env
uvicorn examples.minimal_app:app --reload
```

在对应模块目录下执行，以便解析包名 `auth` / `usage`。

## 新增模块（贡献）

若希望增加新的 `*_module/`，请遵循：独立 `README`、`requirements.txt`、`env.example`、无业务硬编码密钥。详见 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 对外发布（可选）

- PyPI：每个包可独立 `pyproject.toml`，包名需全局唯一。
