# agenmod

可复用的 FastAPI 组件集合（**并行摘录包**）：用户认证、LLM 用量额度等，便于在新项目中**直接复制目录**接入，减少重复造轮子与无效上下文消耗。

## 目标

- **社区协作**：欢迎提交改进与文档，让常见后端能力可被一致、透明地复用。
- **降低浪费**：在 vibe coding / AI 辅助开发时，用成熟模块替代从零生成大段重复代码，**减少 Token 与重复试错**。
- **边界清晰**：各模块自成体系（`README`、`env.example`、SQL）；接入方按需拷贝，配置用环境变量占位。

本仓库**不包含**业务项目骨架；请把子目录复制到你的应用中并按各模块 `INTEGRATION` 文档接入。

## 包含模块

| 目录 | 说明 |
|------|------|
| [auth_module](auth_module/) | 注册、登录、忘记/重置密码、可选 JWT |
| [usage_module](usage_module/) | 按用户 LLM Token 限额、`check_quota` / `record_usage` |

总览与扩展方式见 [docs/MODULES.md](docs/MODULES.md)。

## 快速开始

```bash
git clone https://github.com/agenmod/agenmod.git
cd agenmod/auth_module   # 或 usage_module
cp env.example .env      # 填写本地占位以外的值，勿提交 .env
pip install -r requirements.txt
# 执行对应 migrations_or_sql，再按 README 挂载路由
```

## 文档

- [docs/MODULES.md](docs/MODULES.md) — 模块清单与约定  
- [docs/SECRET_POLICY.md](docs/SECRET_POLICY.md) — 密钥与 `.env`  
- [CONTRIBUTING.md](CONTRIBUTING.md) — 如何贡献  
- [SECURITY.md](SECURITY.md) — 漏洞报告  

## 许可证

MIT License — 见 [LICENSE](LICENSE)。
