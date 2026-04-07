# 将本仓库推送到 GitHub（维护者：agenmod）

本地若已登录其他 GitHub 账号，无法用 `gh repo create agenmod/agenmod` 代建。任选其一：

## 方式 A：使用 GitHub CLI 切换为 agenmod

```bash
gh auth login -h github.com
# 浏览器或 Token 登录 **agenmod** 账号后：
cd /path/to/agenmod
gh repo create agenmod/agenmod --public --source=. --remote=origin --push \
  --description "Reusable FastAPI modules: auth, LLM usage quota."
```

## 方式 B：网页创建空仓库后推送

1. 用 **agenmod** 登录 GitHub → New repository → 仓库名 `agenmod` → Public → 不要勾选 Initialize with README。
2. 本地执行：

```bash
cd /path/to/agenmod
git remote add origin https://github.com/agenmod/agenmod.git
git branch -M main
git push -u origin main
```

（若使用 SSH：`git@github.com:agenmod/agenmod.git`）

## 安全

- **切勿**将 Personal Access Token 写入仓库、Issue 或聊天。
- 若 Token 曾泄露，请在 GitHub → Settings → Developer settings → Personal access tokens 中**立即撤销**并重新生成。
