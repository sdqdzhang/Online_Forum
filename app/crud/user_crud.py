from models import User
from schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import select
async def create_user(db : AsyncSession,user_in: UserCreate,hashed_password: str):
    user_data = user_in.model_dump(exclude={"password"})
    # 默认权限是3
    user_data["created_at"] = datetime.utcnow()
    user_data["role_id"] = 3
    user_data["hashed_password"] = hashed_password
    new_user = User(**user_data)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        raise e

async def get_user_by_email(db : AsyncSession,email:str):
    stmt=select(User).where(User.email==email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user

async def get_user_by_username(db : AsyncSession,username:str):
    stmt=select(User).where(User.username==username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user


