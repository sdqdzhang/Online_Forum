from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core import get_db
from app.services import create_user_service,authenticate_user_service
from app.utils import create_access_token
from schemas import UserCreate,UserRead

router = APIRouter()

@router.post('/register',response_model=UserRead,status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate,db: AsyncSession = Depends(get_db)):
    return await create_user_service(db,user_in)

@router.post('/login')
async def login(login_id: str,password:str,db: AsyncSession = Depends(get_db)):
    user=await authenticate_user_service(db,login_id,password)
    access_token = create_access_token({"sub":user.username})
    return {
        "access_token":access_token,
        "token_type":"Bearer"
    }