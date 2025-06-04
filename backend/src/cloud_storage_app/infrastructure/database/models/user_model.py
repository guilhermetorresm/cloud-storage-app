"""
Modelo SQLAlchemy para a entidade User.
Mapeia a entidade de domínio para a estrutura do banco PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    String, Boolean, DateTime, Text, 
    func, UUID as SQLAlchemy_UUID
)
from sqlalchemy.orm import Mapped, mapped_column

from ..connection import Base


class UserModel(Base):
    """Modelo SQLAlchemy para User"""
    
    __tablename__ = "users"
    
    # Chave primária usando UUID
    id: Mapped[str] = mapped_column(
        SQLAlchemy_UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="Identificador único do usuário"
    )
    
    # Dados de identificação (únicos)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Nome de usuário único"
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email único do usuário"
    )
    
    # Dados de autenticação
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Senha hasheada do usuário"
    )
    
    # Dados pessoais
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Primeiro nome do usuário"
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Sobrenome do usuário"
    )
    
    profile_picture: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL ou caminho da foto de perfil"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição/bio do usuário"
    )
    
    # Controle de estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica se o usuário está ativo"
    )
    
    # Timestamps automáticos
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data de criação"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Data da última atualização"
    )
    
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data do último login"
    )
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username={self.username}, email={self.email})>"
    