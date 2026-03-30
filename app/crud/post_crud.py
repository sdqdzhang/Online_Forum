from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Post, PostLike
from app.schemas import PostCreate


async def create_post(db: AsyncSession, author_id: int, post_in: PostCreate) -> Post:
    post = Post(author_id=author_id, title=post_in.title, content=post_in.content)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def upsert_like(db: AsyncSession, post_id: int, user_id: int) -> bool:
    stmt = select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == user_id)
    result = await db.execute(stmt)
    liked = result.scalars().first()
    if liked:
        return False

    db.add(PostLike(post_id=post_id, user_id=user_id))
    await db.execute(update(Post).where(Post.id == post_id).values(like_count=Post.like_count + 1))
    await db.commit()
    return True


async def get_like_count(db: AsyncSession, post_id: int) -> int:
    stmt = select(func.count(PostLike.id)).where(PostLike.post_id == post_id)
    result = await db.execute(stmt)
    return int(result.scalar() or 0)
