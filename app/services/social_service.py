from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import create_post, get_post_by_id
from app.schemas import PostCreate
from app.services.cache_service import (
    cache_get_with_logical_expire,
    cache_set_with_logical_expire,
    acquire_rebuild_lock,
    release_rebuild_lock,
)
from app.services.hot_rank_service import update_post_hot_score, get_hot_posts
from app.core import get_redis
from app.tasks.social_tasks import persist_like_task


def _post_cache_key(post_id: int) -> str:
    return f"post:{post_id}:detail"


def _post_like_count_key(post_id: int) -> str:
    return f"post:{post_id}:like_count"


def _post_like_user_set_key(post_id: int) -> str:
    return f"post:{post_id}:users"


def _post_lock_key(post_id: int) -> str:
    return f"lock:post:{post_id}:rebuild"


async def create_post_service(db: AsyncSession, author_id: int, post_in: PostCreate):
    post = await create_post(db, author_id, post_in)
    payload = {
        "id": post.id,
        "author_id": post.author_id,
        "title": post.title,
        "content": post.content,
        "like_count": post.like_count,
        "created_at": post.created_at.isoformat(),
    }
    await cache_set_with_logical_expire(_post_cache_key(post.id), payload)
    redis_client = get_redis()
    await redis_client.set(_post_like_count_key(post.id), post.like_count)
    await update_post_hot_score(post.id, post.like_count, post.created_at)
    return post


async def get_post_detail_service(db: AsyncSession, post_id: int) -> dict:
    key = _post_cache_key(post_id)
    cache_data, expired = await cache_get_with_logical_expire(key)
    if cache_data and not expired:
        return cache_data

    if cache_data and expired:
        lock_key = _post_lock_key(post_id)
        if await acquire_rebuild_lock(lock_key):
            try:
                post = await get_post_by_id(db, post_id)
                if post:
                    refreshed = {
                        "id": post.id,
                        "author_id": post.author_id,
                        "title": post.title,
                        "content": post.content,
                        "like_count": post.like_count,
                        "created_at": post.created_at.isoformat(),
                    }
                    await cache_set_with_logical_expire(key, refreshed)
                    return refreshed
            finally:
                await release_rebuild_lock(lock_key)
        return cache_data

    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    payload = {
        "id": post.id,
        "author_id": post.author_id,
        "title": post.title,
        "content": post.content,
        "like_count": post.like_count,
        "created_at": post.created_at.isoformat(),
    }
    await cache_set_with_logical_expire(key, payload)
    return payload


async def like_post_service(db: AsyncSession, post_id: int, user_id: int) -> tuple[bool, int]:
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    redis_client = get_redis()
    user_set_key = _post_like_user_set_key(post_id)
    is_member = await redis_client.sismember(user_set_key, str(user_id))
    if is_member:
        like_count = int(await redis_client.get(_post_like_count_key(post_id)) or post.like_count)
        return False, like_count

    await redis_client.sadd(user_set_key, str(user_id))
    like_count = int(await redis_client.incr(_post_like_count_key(post_id)))
    await update_post_hot_score(post_id=post_id, like_count=like_count, created_at=post.created_at)
    persist_like_task.delay(post_id=post_id, user_id=user_id)

    detail = await get_post_detail_service(db, post_id)
    detail["like_count"] = like_count
    await cache_set_with_logical_expire(_post_cache_key(post_id), detail)
    return True, like_count


async def get_hot_posts_service(limit: int = 20) -> list[dict]:
    items = await get_hot_posts(limit)
    return [{"post_id": post_id, "score": score} for post_id, score in items]
