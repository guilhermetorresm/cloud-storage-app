"""
Modelo base para todos os modelos SQLAlchemy.
Inclui campos comuns e métodos utilitários.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Classe base para todos os modelos SQLAlchemy.
    Inclui campos comuns como id, created_at, updated_at.
    """
    
    # Configuração de tipos para PostgreSQL
    type_annotation_map = {
        str: String().with_variant(String(255), "postgresql"),
    }


class BaseModel(Base):
    """
    Modelo base abstrato com campos comuns.
    Todos os modelos devem herdar desta classe.
    """
    
    __abstract__ = True
    
    # ID único usando UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Timestamps automáticos
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Atualiza o modelo a partir de um dicionário"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ('id', 'created_at'):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """Representação string do modelo"""
        class_name = self.__class__.__name__
        return f"<{class_name}(id={self.id})>"
    
    def __eq__(self, other: object) -> bool:
        """Comparação de igualdade baseada no ID"""
        if not isinstance(other, BaseModel):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash baseado no ID"""
        return hash(self.id)