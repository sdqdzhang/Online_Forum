import asyncio
from app.core.config import Settings
from app.core.db import AsyncSessionLocal, engine
from app.models import Role, Base
from sqlalchemy import select, text

settings = Settings()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully")

async def init_base_data():
    async with AsyncSessionLocal() as db:
        try:
            roles = [
                Role(id=1, name="admin", description="管理员", permissions=["all"]),
                Role(id=2, name="moderator", description="版主",
                     permissions=["login", "post", "comment", "delete_post"]),
                Role(id=3, name="user", description="普通用户", permissions=["login", "post", "comment"]),
                Role(id=4, name="muted", description="被禁言", permissions=["login"]),
                Role(id=5, name="banned", description="被封禁", permissions=[])
            ]
            for role in roles:
                result = await db.execute(select(Role).where(Role.id == role.id))
                if not result.scalars().first():
                    db.add(role)
            await db.commit()
        except Exception as e:
            await db.rollback()
            print("数据初始化失败:", e)


async def fix_legacy_schema():
    async with engine.begin() as conn:
        # 1. 修复 is_active
        result = await conn.execute(text("SHOW COLUMNS FROM posts LIKE 'is_active'"))
        exists = result.first()
        if not exists:
            await conn.execute(text("ALTER TABLE posts ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1"))
            print("Schema fixed: posts.is_active added")

        # 2. 修复 view_count
        result = await conn.execute(text("SHOW COLUMNS FROM posts LIKE 'view_count'"))
        view_exists = result.first()
        if not view_exists:
            await conn.execute(text("ALTER TABLE posts ADD COLUMN view_count INT NOT NULL DEFAULT 0"))
            print("Schema fixed: posts.view_count added")

        # 3. 修复 comment_count
        result = await conn.execute(text("SHOW COLUMNS FROM posts LIKE 'comment_count'"))
        comment_exists = result.first()
        if not comment_exists:
            await conn.execute(text("ALTER TABLE posts ADD COLUMN comment_count INT NOT NULL DEFAULT 0"))
            print("Schema fixed: posts.comment_count added")

        # 4. 修复 updated_at（这次报错的字段）
        result = await conn.execute(text("SHOW COLUMNS FROM posts LIKE 'updated_at'"))
        updated_exists = result.first()
        if not updated_exists:
            await conn.execute(text(
                "ALTER TABLE posts ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            ))
            print("Schema fixed: posts.updated_at added")

        # 统一强制设置所有字段的默认值（彻底根治）
        await conn.execute(text("ALTER TABLE posts MODIFY COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1"))
        await conn.execute(text("ALTER TABLE posts MODIFY COLUMN like_count INT NOT NULL DEFAULT 0"))
        await conn.execute(text("ALTER TABLE posts MODIFY COLUMN view_count INT NOT NULL DEFAULT 0"))
        await conn.execute(text("ALTER TABLE posts MODIFY COLUMN comment_count INT NOT NULL DEFAULT 0"))
        await conn.execute(text("ALTER TABLE posts MODIFY COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

async def init_database():
    await create_tables()
    await fix_legacy_schema()
    await init_base_data()

if __name__ == '__main__':
    asyncio.run(init_database())
