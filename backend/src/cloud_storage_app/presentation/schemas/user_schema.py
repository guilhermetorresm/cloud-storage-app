# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para criação de usuário"""
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    """Schema para login de usuário"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema para resposta do usuário"""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema para token de acesso"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema para dados do token"""
    username: Optional[str] = None
