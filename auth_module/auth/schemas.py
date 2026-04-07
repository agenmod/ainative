"""请求/响应模型"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    gender: Optional[str] = "other"  # male / female / other
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    hometown: Optional[str] = None
    current_city: Optional[str] = None
    interests: Optional[List[str]] = None
    behavior_token: Optional[str] = None
    verify_token: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str
    behavior_token: Optional[str] = None
    verify_token: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    gender: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    hometown: Optional[str] = None
    current_city: Optional[str] = None
    interests: Optional[str] = None
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
