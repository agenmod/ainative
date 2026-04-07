"""
精简限流 + 登录锁定（仅依赖 Redis）
未配置 REDIS_URL 时所有检查放行。
"""
from typing import Dict, Tuple

from auth.redis_client import get_redis

RATE_LIMITS = {
    "register": (3, 3600),
    "forgot_pwd": (5, 3600),
    "login": (10, 60),
}

LOGIN_MAX_FAILURES = 5
LOGIN_LOCK_SECONDS = 900


def check_rate_limit(action: str, identifier: str) -> Tuple[bool, Dict]:
    r = get_redis()
    if not r:
        return True, {"remaining": 999}
    rule = RATE_LIMITS.get(action)
    if not rule:
        return True, {"remaining": 999}
    max_count, window = rule
    key = f"rl:{action}:{identifier}"
    try:
        current = r.get(key)
        count = int(current) if current else 0
        if count >= max_count:
            ttl = r.ttl(key)
            return False, {"remaining": 0, "retry_after": max(ttl, 1)}
        pipe = r.pipeline()
        pipe.incr(key)
        if count == 0:
            pipe.expire(key, window)
        pipe.execute()
        return True, {"remaining": max_count - count - 1}
    except Exception:
        return True, {"remaining": 999}


def check_login_lock(ip: str) -> Tuple[bool, int]:
    r = get_redis()
    if not r:
        return False, 0
    try:
        ttl = r.ttl(f"login_lock:{ip}")
        if ttl and ttl > 0:
            return True, ttl
    except Exception:
        pass
    return False, 0


def record_login_failure(ip: str):
    r = get_redis()
    if not r:
        return
    try:
        fail_key = f"login_fail:{ip}"
        lock_key = f"login_lock:{ip}"
        count = r.incr(fail_key)
        if count == 1:
            r.expire(fail_key, 300)
        if count >= LOGIN_MAX_FAILURES:
            r.setex(lock_key, LOGIN_LOCK_SECONDS, "1")
            r.delete(fail_key)
    except Exception:
        pass


def clear_login_failures(ip: str):
    r = get_redis()
    if not r:
        return
    try:
        r.delete(f"login_fail:{ip}")
    except Exception:
        pass


def protect_endpoint(
    action: str,
    ip: str,
    user_id: str = None,
    behavior_token: str = None,
) -> Dict:
    """
    统一防护：登录锁定 + 限流。
    不包含行为评分/滑动验证（可选扩展）。
    """
    if action == "login":
        locked, remaining = check_login_lock(ip)
        if locked:
            return {
                "allowed": False,
                "reason": "locked",
                "retry_after": remaining,
                "message": f"登录失败次数过多，请 {remaining} 秒后再试",
            }
    allowed, info = check_rate_limit(action, user_id or ip)
    if not allowed:
        return {
            "allowed": False,
            "reason": "rate_limit",
            "retry_after": info.get("retry_after", 60),
            "message": "操作过于频繁，请稍后再试",
        }
    return {"allowed": True}
