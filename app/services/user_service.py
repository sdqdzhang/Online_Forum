from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate
from app.utils.security import get_password_hash, verify_password
from app.crud import get_user_by_username, create_user,get_user_by_email

async def create_user_service(db: AsyncSession, user_data: UserCreate):
    # 1. 检查冲突 (业务逻辑)
    # 提示: 可以在这里调用 crud.get_user_by_username
    user =await get_user_by_username(db,user_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被注册"
        )
    hashed_password = get_password_hash(user_data.password)
    new_user=await create_user(db, user_data, hashed_password)
    return new_user


async def authenticate_user_service(db: AsyncSession, login_id, password):
    user = await get_user_by_username(db,login_id)
    if not user and '@' in login_id:
        user = await get_user_by_email(db,login_id)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确"
        )
    return user


    # 1. 获取用户
    # 2. 校验密码
    # 3. 返回用户或抛出错误
# 用户名中不能带特殊字符，比如@，会导致校验出问题