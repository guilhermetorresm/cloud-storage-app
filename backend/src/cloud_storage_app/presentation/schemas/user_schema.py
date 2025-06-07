# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreateSchema(BaseModel):
    """Schema para criação de usuário.
    
    Attributes:
        username: Nome de usuário único (3-30 caracteres)
        email: Email válido e único
        password: Senha (mínimo 8 caracteres)
        first_name: Nome do usuário (1-50 caracteres)
        last_name: Sobrenome do usuário (opcional, máximo 50 caracteres)
    """
    username: str = Field(..., min_length=3, max_length=30, description="Nome de usuário único")
    email: EmailStr = Field(..., description="Email válido e único")
    password: str = Field(..., min_length=8, description="Senha com mínimo de 8 caracteres")
    first_name: str = Field(..., min_length=1, max_length=50, description="Nome do usuário")
    last_name: Optional[str] = Field(None, max_length=50, description="Sobrenome do usuário (opcional)")


class UserUpdateSchema(BaseModel):
    """Schema para atualização de usuário.
    
    Attributes:
        first_name: Novo nome do usuário (opcional)
        last_name: Novo sobrenome do usuário (opcional)
        email: Novo email (opcional)
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseModel):
    """Schema para resposta de usuário.
    
    Attributes:
        user_id: ID único do usuário
        username: Nome de usuário
        email: Email do usuário
        first_name: Nome do usuário
        last_name: Sobrenome do usuário (opcional)
        profile_picture: URL da foto de perfil (opcional)
        description: Descrição do usuário (opcional)
        created_at: Data de criação
        updated_at: Data da última atualização
        last_login_at: Data do último login (opcional)
        is_active: Status de ativação do usuário
    """
    user_id: str
    username: str
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserSimpleResponseSchema(BaseModel):
    """Schema para resposta simplificada de usuário.
    
    Attributes:
        user_id: ID único do usuário
        username: Nome de usuário
        email: Email do usuário
        first_name: Nome do usuário
        last_name: Sobrenome do usuário (opcional)
    """
    user_id: str
    username: str
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserLoginSchema(BaseModel):
    """Schema para login de usuário.
    
    Attributes:
        username: Nome de usuário ou email
        password: Senha do usuário
    """
    username: str = Field(..., description="Nome de usuário ou email")
    password: str = Field(..., min_length=8, description="Senha do usuário")


class UserLoginResponseSchema(BaseModel):
    """Schema para resposta de login.
    
    Attributes:
        user: Dados do usuário
        access_token: Token de acesso JWT
        refresh_token: Token de atualização JWT
    """
    user: UserSimpleResponseSchema
    access_token: str
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordSchema(BaseModel):
    """Schema para mudança de senha.
    
    Attributes:
        current_password: Senha atual
        new_password: Nova senha
    """
    current_password: str = Field(..., min_length=8, description="Senha atual")
    new_password: str = Field(..., min_length=8, description="Nova senha")


class Token(BaseModel):
    """Schema para token de acesso"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponseSchema

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Schema para dados do token"""
    username: Optional[str] = None
