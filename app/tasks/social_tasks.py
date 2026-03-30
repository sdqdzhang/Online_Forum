import asyncio
from app.core import celery_app, AsyncSessionLocal
from app.crud import upsert_like


@celery_app.task(name="tasks.persist_like_task", autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def persist_like_task(post_id: int, user_id: int) -> bool:
    return asyncio.run(_persist_like(post_id=post_id, user_id=user_id))


async def _persist_like(post_id: int, user_id: int) -> bool:
    async with AsyncSessionLocal() as db:
        return await upsert_like(db=db, post_id=post_id, user_id=user_id)
