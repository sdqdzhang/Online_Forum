import math
from datetime import datetime
from app.core import get_redis, settings


def calculate_hot_score(like_count: int, created_at: datetime) -> float:
    age_hours = max((datetime.utcnow() - created_at).total_seconds() / 3600.0, 1.0)
    interaction_score = like_count * 1.0
    return interaction_score / math.pow(age_hours, 0.8)


async def update_post_hot_score(post_id: int, like_count: int, created_at: datetime) -> float:
    redis_client = get_redis()
    score = calculate_hot_score(like_count=like_count, created_at=created_at)
    await redis_client.zadd(settings.hot_rank_key, {str(post_id): score})
    return score


async def get_hot_posts(limit: int = 20) -> list[tuple[int, float]]:
    redis_client = get_redis()
    result = await redis_client.zrevrange(settings.hot_rank_key, 0, limit - 1, withscores=True)
    return [(int(post_id), float(score)) for post_id, score in result]
