import json
from datetime import datetime, timedelta
from app.core import get_redis, settings


async def cache_set_with_logical_expire(key: str, payload: dict, expire_seconds: int | None = None) -> None:
    expire_seconds = expire_seconds or settings.cache_logical_expire_seconds
    logical_expire_at = datetime.utcnow() + timedelta(seconds=expire_seconds)
    wrapped = {
        "data": payload,
        "logical_expire_at": logical_expire_at.isoformat(),
    }
    redis_client = get_redis()
    await redis_client.set(key, json.dumps(wrapped), ex=settings.cache_ttl_seconds)


async def cache_get_with_logical_expire(key: str) -> tuple[dict | None, bool]:
    redis_client = get_redis()
    raw = await redis_client.get(key)
    if not raw:
        return None, True

    wrapped = json.loads(raw)
    expire_at = datetime.fromisoformat(wrapped["logical_expire_at"])
    is_expired = datetime.utcnow() >= expire_at
    return wrapped.get("data"), is_expired


async def acquire_rebuild_lock(lock_key: str) -> bool:
    redis_client = get_redis()
    return bool(await redis_client.set(lock_key, "1", ex=settings.cache_lock_seconds, nx=True))


async def release_rebuild_lock(lock_key: str) -> None:
    redis_client = get_redis()
    await redis_client.delete(lock_key)
