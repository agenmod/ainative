# 推送与远程仓库

默认远程为 **`Chiody/ainative`**（与当前常用 GitHub 账号一致）。若你使用其他账号或组织，请替换下面的 owner/repo。

## 使用 GitHub CLI 创建并推送

```bash
cd /path/to/ainative
gh repo create Chiody/ainative --public --source=. --remote=origin --push \
  --description "Ainative: reusable FastAPI modules for AI-native apps (auth, LLM quota)."
```

若本地已有 `origin`，可先：`git remote remove origin`。

## 网页创建空仓库后推送

1. 在 GitHub 上新建仓库 **`ainative`**（Public，不要勾选 README）。
2. `git remote add origin https://github.com/<你的用户名>/ainative.git`
3. `git branch -M main && git push -u origin main`

## 安全

勿将 Personal Access Token 写入仓库；勿提交 `.env`。
