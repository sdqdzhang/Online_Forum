import asyncio
from app.core.init_db import init_database


async def main() -> None:
    print("[prestart] 开始初始化数据库...")
    await init_database()
    print("[prestart] 初始化完成。")


if __name__ == "__main__":
    asyncio.run(main())
