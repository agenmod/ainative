# 前端：如何存储用户/Token 与发送请求

## 简单模式（仅 user，请求带 user_id）

- 登录成功后，接口返回**用户对象**，前端将其存入 `localStorage`：
  ```js
  const d = await response.json();
  localStorage.setItem('user', JSON.stringify(d));
  window.user = d;
  ```
- 需要“当前用户”的接口，在 **body 或 query** 中带上 `user_id: user.id`（或 `user_id=xxx`）。服务端不校验该 user_id 是否来自合法登录态。
- 退出：`localStorage.removeItem('user'); user = null;`

## JWT 模式（Token + Authorization 头）

- 登录成功后，接口返回 `access_token` 和用户信息。前端保存两者：
  ```js
  localStorage.setItem('user', JSON.stringify(d));
  localStorage.setItem('access_token', d.access_token);
  ```
- 请求需要鉴权的接口时，在 **Header** 中带上：
  ```js
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
  }
  ```
- 若接口返回 **401**，表示未登录或 token 过期，应清除本地 user 与 token 并跳转登录：
  ```js
  if (response.status === 401) {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    window.user = null;
    showLogin(); // 或跳转登录页
  }
  ```
- 获取当前用户信息：`GET /api/v1/users/me`，Header 带 `Authorization: Bearer <token>`。

## 重置密码页

- 路由约定：`#/reset-password/:token`（例如从邮件链接进入）。
- 进入页面前先请求 `GET /api/v1/users/check-reset-token/{token}`，若返回 `{ valid: true }` 再展示“设置新密码”表单。
- 提交新密码：`POST /api/v1/users/reset-password`，body `{ token, new_password }`。
