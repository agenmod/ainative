# Ainative

**AI-native** 场景下的可复用 **FastAPI** 组件库：用户认证、LLM 用量额度等。将子目录复制到你的项目即可接入，减少重复实现与无效上下文消耗。

## 目标

- **社区协作**：改进文档与模块，让常见后端能力可一致复用。
- **降低浪费**：在 vibe coding / AI 辅助开发时，用成熟模块替代从零生成大段重复代码。
- **边界清晰**：各模块自带 `README`、`env.example`、SQL；配置走环境变量占位。

本仓库**不包含**完整业务骨架；请按各模块的 `*_INTEGRATION.md` 接入。

## 包含模块

| 目录 | 说明 |
|------|------|
| [auth_module](auth_module/) | 注册、登录、忘记/重置密码、可选 JWT |
| [usage_module](usage_module/) | 按用户 LLM Token 限额、`check_quota` / `record_usage` |

总览见 [docs/MODULES.md](docs/MODULES.md)。

## 快速开始

```bash
git clone https://github.com/agenmod/ainative.git
cd ainative/auth_module   # 或 usage_module
cp env.example .env       # 本地填写真实值，勿提交 .env
pip install -r requirements.txt
# 执行 migrations_or_sql，再按 README 挂载路由
```

## 文档

- [docs/MODULES.md](docs/MODULES.md) — 模块清单与约定  
- [docs/SECRET_POLICY.md](docs/SECRET_POLICY.md) — 密钥与 `.env`  
- [CONTRIBUTING.md](CONTRIBUTING.md) — 如何贡献  
- [SECURITY.md](SECURITY.md) — 漏洞报告  
- [docs/PUBLISH.md](docs/PUBLISH.md) — 维护者推送说明  

## 许可证

MIT License — 见 [LICENSE](LICENSE)。

> **FastAPI** 为独立项目；本仓库为社区模块集合，**非 FastAPI 官方**。
