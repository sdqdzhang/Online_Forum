from jose import JWTError
from app.crud import get_user_by_username
from app.utils import decode_token
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from app.core import get_db
from app.schemas import UserRead

router = APIRouter()
oauth = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
async def get_user_by_token(db:AsyncSession=Depends(get_db),token:str=Depends(oauth)) -> User:
    try:
        payload=decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token error")
        username=payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail="Token error")
        user=await get_user_by_username(db, username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return user

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_user_by_token)):
    return current_user
