from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class CreateUserDTO(BaseModel):
    """DTO para criação de usuários."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UpdateUserDTO(BaseModel):
    """DTO para atualização de usuários."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    email: Optional[EmailStr] = None


class ChangePasswordDTO(BaseModel):
    """DTO para mudança de senha."""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class UserResponseDTO(BaseModel):
    """DTO para resposta de usuários."""
    user_id: str
    username: str
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class UserResponseSimpleDTO(BaseModel):
    """DTO para resposta de usuários simples."""
    user_id: str
    username: str
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr

    class Config:
        from_attributes = True


class UserLoginDTO(BaseModel):
    """DTO para login de usuários."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLoginResponseDTO(BaseModel):
    """DTO para resposta de login de usuários."""
    user: UserResponseSimpleDTO
    access_token: str
    refresh_token: str
    token_type: str

    class Config:
        from_attributes = True
