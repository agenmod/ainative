# 前端展示额度示例

接入方在「设置页」或「用量页」请求 `GET /api/v1/me/quota` 或 `GET /api/v1/users/{user_id}/quota`，用返回的 `used` / `limit` / `remaining` 展示进度条与文案。

## 请求

```javascript
const API = 'https://your-api.com/api/v1';
const user = JSON.parse(localStorage.getItem('user') || '{}'); // 或从 JWT 解析

// 方式一：当前用户（需后端注入 get_current_user_id，且请求带 Authorization）
const r = await fetch(`${API}/me/quota`, {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
});

// 方式二：传 user_id（如前端存了 user.id）
const r = await fetch(`${API}/users/${user.id}/quota`);
const q = await r.json();
```

## 响应结构

```json
{
  "used": 12000,
  "limit": 500000,
  "remaining": 488000,
  "subscription_tier": "free"
}
```

## 简单 HTML + JS 片段（进度条 + 文案）

```html
<div id="quota-area">
  <div class="quota-bar-wrap">
    <span class="quota-label">平台免费额度</span>
    <span class="quota-value" id="quota-value">-- / -- tokens</span>
  </div>
  <div class="quota-bar">
    <div class="quota-fill" id="quota-fill"></div>
  </div>
  <div class="quota-hint" id="quota-hint">加载中...</div>
</div>

<script>
(async function () {
  const API = '/api/v1';
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  if (!user.id) { document.getElementById('quota-hint').textContent = '请先登录'; return; }
  try {
    const r = await fetch(`${API}/users/${user.id}/quota`);
    const q = await r.json();
    const pct = q.limit > 0 ? Math.round(q.used / q.limit * 100) : 0;
    const color = pct > 80 ? '#ef4444' : (pct > 50 ? '#f59e0b' : 'var(--green, #22c55e)');
    document.getElementById('quota-value').textContent =
      (q.used || 0).toLocaleString() + ' / ' + (q.limit || 500000).toLocaleString() + ' tokens';
    const fill = document.getElementById('quota-fill');
    fill.style.width = Math.min(pct, 100) + '%';
    fill.style.background = color;
    document.getElementById('quota-hint').textContent =
      '剩余 ' + (q.remaining || 0).toLocaleString() + ' tokens，当前免费使用。';
  } catch (e) {
    document.getElementById('quota-hint').textContent = '加载失败';
  }
})();
</script>

<style>
.quota-bar-wrap { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.quota-bar { height: 6px; background: rgba(255,255,255,.06); border-radius: 3px; overflow: hidden; }
.quota-fill { height: 100%; border-radius: 3px; transition: width .3s; }
.quota-hint { font-size: 12px; color: var(--txF, #6b7280); margin-top: 6px; }
</style>
```

按需替换 `API`、`user` 来源（localStorage / JWT / 当前路由）及样式变量。
