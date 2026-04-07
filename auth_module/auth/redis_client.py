"""Redis 连接（可选）；未配置 REDIS_URL 时返回 None"""
_redis = None


def get_redis():
    global _redis
    if _redis is not None:
        return _redis
    from auth.config import settings
    if not settings.REDIS_URL:
        return None
    try:
        import redis
        _redis = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        _redis.ping()
        return _redis
    except Exception:
        return None
