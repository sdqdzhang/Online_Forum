import os
from app.core.config import Settings
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import  AsyncEngine,AsyncSession,async_sessionmaker,create_async_engine
from sqlalchemy import text

settings = Settings()
base_url = settings.database_url
DB_POOL_SIZE = settings.DB_POOL_SIZE
DB_MAX_OVERFLOW = settings.DB_MAX_OVERFLOW
DB_POOL_RECYCLE = settings.DB_POOL_RECYCLE
DB_ECHO = settings.debug

engine :AsyncEngine = create_async_engine(
    url=base_url,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE,
    echo=DB_ECHO,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

async def get_db() ->AsyncGenerator[AsyncSession, None] :
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


async def test_get_db():
    try:
        async for db in get_db():
            result= await db.execute(text("select * from users"))
            scalar_result=result.mappings().all()
            print(scalar_result)
    except Exception as e:
        print(e)

import asyncio
if __name__ == '__main__':
    asyncio.run(test_get_db())


