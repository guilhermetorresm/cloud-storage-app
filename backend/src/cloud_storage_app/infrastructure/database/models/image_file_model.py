"""
Modelo SQLAlchemy para a entidade ImageFile.
Mapeia a entidade de domínio para a estrutura do banco PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    String, Boolean, DateTime, Text, Integer, BigInteger, Float,
    func, UUID as SQLAlchemy_UUID, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..connection import Base


class ImageFileModel(Base):
    """Modelo SQLAlchemy para ImageFile"""
    
    __tablename__ = "image_files"
    
    # Chave primária usando UUID
    id: Mapped[str] = mapped_column(
        SQLAlchemy_UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="Identificador único do arquivo de imagem"
    )
    
    # Chave estrangeira para o usuário proprietário
    owner_id: Mapped[str] = mapped_column(
        SQLAlchemy_UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do usuário proprietário"
    )
    
    # Dados básicos do arquivo
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome do arquivo"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Descrição do arquivo"
    )
    
    path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Caminho do arquivo no sistema"
    )
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Tipo MIME do arquivo"
    )
    
    extension: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Extensão do arquivo"
    )
    
    category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Categoria do arquivo (audio, image, video)"
    )
    
    size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="Tamanho do arquivo em bytes"
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
    
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data do último acesso"
    )
    
    # Tags (armazenadas como JSON ou texto separado por vírgulas)
    tags: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Tags do arquivo separadas por vírgulas"
    )
    
    # Metadados específicos de imagem
    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Largura da imagem em pixels"
    )
    
    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Altura da imagem em pixels"
    )
    
    color_depth: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Profundidade de cor (bits por pixel)"
    )
    
    dpi: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Resolução em DPI"
    )
    
    has_transparency: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Indica se a imagem possui transparência"
    )
    
    compression: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo de compressão da imagem"
    )
    
    # Metadados EXIF da câmera
    camera_make: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Fabricante da câmera"
    )
    
    camera_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Modelo da câmera"
    )
    
    taken_at: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Data/hora da foto em formato ISO"
    )
    
    # Dados GPS
    gps_latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Latitude GPS"
    )
    
    gps_longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Longitude GPS"
    )
    
    # Thumbnail
    thumbnail: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Caminho do thumbnail da imagem"
    )
    
    # Controle de estado
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica se o arquivo foi deletado (soft delete)"
    )
    
    # Relacionamentos
    owner = relationship("UserModel", back_populates="image_files")
    
    def __repr__(self) -> str:
        return f"<ImageFileModel(id={self.id}, name={self.name}, owner_id={self.owner_id})>"