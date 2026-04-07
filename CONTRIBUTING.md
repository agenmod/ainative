# 贡献指南

感谢参与 **agenmod**：目标是让常见后端能力可被透明复用，减少各项目重复实现与无效 Token 消耗。

## 贡献范围

- **已有模块**：修 bug、补测试、改进文档、`env.example` 与集成说明。
- **新模块**：新增 `your_module/` 目录，包含 `README.md`、`requirements.txt`、`env.example`、可选 `migrations_or_sql/` 与 `examples/minimal_app.py`；避免硬编码密钥与仅个人业务可用的常量。

## 提交规范

- 勿提交 `.env` 或任何密钥；见 [docs/SECRET_POLICY.md](docs/SECRET_POLICY.md)。
- 文档与注释使用清晰、可翻译的中文或英文均可，保持与现有风格一致。

## 问题与安全

- 一般问题：使用 GitHub Issues。
- 安全漏洞：见 [SECURITY.md](SECURITY.md)，勿在公开 Issue 中披露利用细节。

## 许可证

提交即表示你同意以 [LICENSE](LICENSE)（MIT）授权你的贡献。
