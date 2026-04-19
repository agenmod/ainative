# Ainative — 项目上下文交接文档

本文件供**后续 AI 或协作者**阅读，完整了解本项目的来龙去脉、当前状态与决策记录。

---

## 1. 项目是什么

**Ainative** 是一个面向 **AI-native（AI 原生）应用**的、可复用的 **FastAPI 后端组件库**。

- **GitHub 仓库**：https://github.com/agenmod/ainative（Public，MIT License）
- **GitHub 账号**：`agenmod`（个人用户，非组织）
- **本地路径**：`/Users/yuanqi/Desktop/AIcode/ainative`
- **技术栈**：Python 3.10+、FastAPI、SQLAlchemy、pydantic-settings、PostgreSQL；Redis 可选

## 2. 为什么做这个项目

### 来源

维护者在开发一个 **AI 社区论坛项目**（私有仓库 `pojie`，路径 `/Users/yuanqi/Desktop/AIcode/pojie`）时，积累了用户认证、LLM 用量额度等通用后端能力。希望将这些能力**提炼为独立可复用模块**，开源给社区。

### 目的

1. **复用**：自己做新项目时，直接复制子目录接入，不必从零重写。
2. **开源**：让其他开发者（尤其 vibe coding / AI 辅助开发场景）也能复用，**减少重复造轮子与无效 Token 消耗**。
3. **社区协作**：吸引贡献者一起丰富模块库，长期目标是成为 **AI 原生应用后端领域**值得信赖的组件集合。

### 关键约束（已确定）

- **与原项目解耦**：`ainative` 仓库里**不体现、不提及**原 `pojie` 项目的存在和关系。对外是独立开源项目。
- **原项目不改 import**：`pojie` 主工程 `ai-service` **不会**改为引用 `ainative` 里的模块包。两条线并行，互不影响。
- **占位型配置**：所有 `env.example`、文档示例一律使用通用占位值（`localhost`、`change-me`），不出现真实密钥或内网地址。

## 3. 当前包含的模块

| 模块 | 目录 | 状态 | 说明 |
|------|------|------|------|
| **用户认证** | `auth_module/` | 可用 | 注册、登录、忘记/重置密码、可选 JWT、限流、bcrypt |
| **LLM 用量 / 额度** | `usage_module/` | 可用 | 按用户 token 限额、`check_quota` / `record_usage`、可选明细表 |

每个模块自成体系：
- `README.md` — 功能与配置说明
- `*_INTEGRATION.md` — 详细接入步骤
- `env.example` — 环境变量模板（全占位）
- `requirements.txt` — 独立依赖
- `migrations_or_sql/` — 建表 SQL
- `examples/minimal_app.py` — 最小可运行示例
- `frontend_snippets/` — 可选前端片段

## 4. 仓库文件结构

```
ainative/
├── README.md                     # 项目首页
├── LICENSE                       # MIT
├── CONTRIBUTING.md               # 贡献指南
├── SECURITY.md                   # 漏洞报告
├── .gitignore
├── docs/
│   ├── MODULES.md                # 模块清单与约定
│   ├── SECRET_POLICY.md          # 密钥管理规范
│   └── PUBLISH.md                # 推送说明（维护者用）
├── auth_module/                  # 用户认证模块
│   ├── auth/                     # Python 包（api, models, config, security…）
│   ├── env.example
│   ├── examples/minimal_app.py
│   ├── migrations_or_sql/
│   ├── frontend_snippets/
│   ├── requirements.txt
│   ├── README.md
│   └── AUTH_INTEGRATION.md
└── usage_module/                 # LLM 用量模块
    ├── usage/                    # Python 包（api, models, config, service, deps…）
    ├── env.example
    ├── examples/minimal_app.py
    ├── migrations_or_sql/
    ├── frontend_snippets/
    ├── requirements.txt
    ├── README.md
    └── USAGE_INTEGRATION.md
```

## 5. 模块设计约定

每个模块遵循以下四条边界：

1. **配置**：仅通过环境变量 + `pydantic-settings`，禁止硬编码密钥或业务域名。
2. **数据**：自带 SQL 迁移；表名可通过配置避免冲突（`usage_module` 用 `USAGE_` 前缀）。
3. **契约**：对外暴露 **HTTP 路由**（FastAPI `router`）+ 可选 **Python API**（如 `check_quota`）；接入方注入 `user_id` / `db`。
4. **依赖**：独立 `requirements.txt`，标注与接入方可能重复的包。

## 6. 品牌与命名决策记录

| 决策点 | 结论 | 原因 |
|--------|------|------|
| GitHub 用户名 | `agenmod` | 维护者已注册 |
| 仓库名 | `ainative` | 短、像品牌词、与 AI-native 直接关联 |
| 对外叙事 | **「Ainative：AI-native 场景下的可复用 FastAPI 组件库」** | 明确领域、技术栈、使用方式 |
| 与 FastAPI 关系 | README 底部注明「非 FastAPI 官方」 | 避免误导 |
| 许可证 | MIT | 最大化复用自由度 |

## 7. 愿景与路线图（讨论中，非承诺）

### 短期（当前）
- 稳定 `auth_module` 和 `usage_module` 的 API 与文档。
- 社区推广：README 英文化、good first issue。

### 中期（按需提炼）
- 从实际 AI 项目经验中再提炼新模块，优先：
  - **调用侧护栏**：按用户/路由的限流与并发上限
  - **可观测最小集**：request id、模型名、token 数、延迟的结构化日志中间件
  - **密钥管理范式**：环境变量约定与可选「只存引用不存明文」的接入说明
- 新模块仍按「复制子目录 + env.example + README」的模式。

### 长期（可选）
- **脚手架 / CLI**：`ainative init` 生成项目骨架（类似 `create-vite`），可选勾选需要的模块。
- **PyPI 发布**：每个模块独立 `pyproject.toml`。
- 演进为社区认可的 **AI 应用后端工程组件标准**。

### 明确不做
- 不替代 LangChain / LlamaIndex / 各模型 SDK（不做模型编排层）。
- 不包含完整业务骨架 / 全栈模板。
- 不在本仓库维护原私有项目 `pojie` 的业务代码。

## 8. 安全与运维备忘

- **GitHub Token**：维护者曾在聊天中暴露过 `agenmod` 的 PAT，**必须已撤销并重新生成**。
- **推送方式**：本地 `gh auth login` 切到 `agenmod` 后 `git push origin main`；或配置 SSH key。
- **密钥规范**：见 `docs/SECRET_POLICY.md`；`.gitignore` 已覆盖 `.env`、`*.pem`、`*.key`。

## 9. 原项目参考（仅供维护者内部使用）

- 原项目路径：`/Users/yuanqi/Desktop/AIcode/pojie`
- 原项目中的对应文件：`pojie/auth_module/`、`pojie/usage_module/`（是 ainative 的来源副本）
- `pojie` 主工程 `ai-service/` 仍用自己的 `app.api.users` 等，**不引用** ainative。
- 若以后想从 `pojie` 再提炼新模块：从 `ai-service/app/` 复制删减到 `ainative/xxx_module/`，`pojie` 不改 import。

## 10. 交接给后续 AI 的操作建议

1. **阅读**本文件 + `README.md` + `docs/MODULES.md` 即可了解全貌。
2. **改代码**前先确认不引入真实密钥、不提及原项目名称或内部 URL。
3. **新增模块**参照 `auth_module` 的目录结构与 `CONTRIBUTING.md` 规范。
4. **推送**用 `agenmod` 账号的凭据（`gh auth login` 或 SSH）；远程 origin 为 `https://github.com/agenmod/ainative.git`。
5. 若需要改仓库设置（如开启 Discussions、Pages），用 `agenmod` 账号在 GitHub 网页操作或 `gh repo edit`。
