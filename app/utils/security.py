from passlib.context import CryptContext
from jose import jwt
from app.core.config import settings
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password :str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


if __name__=="__main__":
    hashed_password = get_password_hash("123456")
    print(get_password_hash("123456"))
    print(verify_password("123456", hashed_password))
    token=create_access_token(data={"username":"test"})
    print(token)
    decoded_data = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    print("解码后的内容：", decoded_data)