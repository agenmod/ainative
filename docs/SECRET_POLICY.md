# 密钥与敏感信息管理

## 禁止提交

- 真实 **`.env`**、API Key、数据库密码、JWT 密钥、私钥（`*.pem`、`*.key`）。
- 本仓库仅保留 **`env.example`** 占位符；本地复制为 `.env` 后填写，**勿** `git add .env`。

## 推荐做法

- 使用 `openssl rand -hex 32` 生成密钥。
- 若误提交密钥，应**轮换密钥**并清理 Git 历史。

## 报告安全问题

见根目录 [SECURITY.md](../SECURITY.md)。
