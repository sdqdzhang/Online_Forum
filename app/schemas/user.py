from pydantic import BaseModel, EmailStr, ConfigDict,Field

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(...,min_length=6,max_length=32)

class UserRead(UserBase):
    id: int
    role_id:int
    model_config = ConfigDict(from_attributes=True)

