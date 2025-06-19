from pydantic import BaseModel, EmailStr
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.user

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ShowUser(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str