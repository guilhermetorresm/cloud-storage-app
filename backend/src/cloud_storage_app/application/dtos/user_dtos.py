from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateUserDTO:
    """DTO para criação de usuários."""
    first_name: str
    last_name: Optional[str] = None
    username: str
    email: str
    password: str


@dataclass
class UpdateUserDTO:
    """DTO para atualização de usuários."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


@dataclass
class ChangePasswordDTO:
    """DTO para mudança de senha."""
    current_password: str
    new_password: str


@dataclass
class UserResponseDTO:
    """DTO para resposta de usuários."""
    user_id: str
    username: str
    first_name: str
    last_name: Optional[str] = None
    email: str
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool

    @classmethod
    def from_entity(cls, user) -> 'UserResponseDTO':
        """Converte uma entidade User em um DTO de resposta."""
        return cls(
            user_id=str(user.user_id),
            username=str(user.username),
            first_name=str(user.first_name),
            last_name=str(user.last_name) if user.last_name else None,
            email=str(user.email),
            profile_picture=str(user.profile_picture) if user.profile_picture else None,
            description=str(user.description) if user.description else None,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            is_active=user.is_active
        )
    

@dataclass
class UserResponseSimpleDTO:
    """DTO para resposta de usuários simples."""
    user_id: str
    username: str
    first_name: str
    last_name: Optional[str] = None
    email: str

    @classmethod
    def from_entity(cls, user) -> 'UserResponseSimpleDTO':
        """Converte uma entidade User em um DTO de resposta simples."""
        return cls(
            user_id=str(user.user_id),
            username=str(user.username),
            first_name=str(user.first_name),
            last_name=str(user.last_name) if user.last_name else None,
            email=str(user.email)
        )
    

@dataclass
class UserLoginDTO:
    """DTO para login de usuários."""
    username: str
    password: str


@dataclass
class UserLoginResponseDTO:
    """DTO para resposta de login de usuários."""
    user: UserResponseSimpleDTO
    access_token: str
    refresh_token: str
