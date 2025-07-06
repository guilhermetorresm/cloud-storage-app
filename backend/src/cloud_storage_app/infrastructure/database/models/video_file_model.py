"""
Modelo SQLAlchemy para a entidade VideoFile.
Mapeia a entidade de domínio para a estrutura do banco PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    String, Boolean, DateTime, Text, Integer, BigInteger, Float,
    func, UUID as SQLAlchemy_UUID, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..connection import Base


class VideoFileModel(Base):
    """Modelo SQLAlchemy para VideoFile"""
    
    __tablename__ = "video_files"
    
    # Chave primária usando UUID
    id: Mapped[str] = mapped_column(
        SQLAlchemy_UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="Identificador único do arquivo de vídeo"
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
    
    # Metadados específicos de vídeo
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Duração do vídeo em segundos"
    )
    
    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Largura do vídeo em pixels"
    )
    
    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Altura do vídeo em pixels"
    )
    
    frame_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Taxa de quadros por segundo (fps)"
    )
    
    bitrate: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Taxa de bits em kbps"
    )
    
    codec: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Codec de vídeo utilizado"
    )
    
    audio_codec: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Codec de áudio utilizado"
    )
    
    has_audio: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Indica se o vídeo possui áudio"
    )
    
    has_subtitles: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Indica se o vídeo possui legendas"
    )
    
    created_with: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Software usado para criar o vídeo"
    )
    
    genre: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Gênero do vídeo"
    )
    
    # Thumbnail
    thumbnail: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Caminho do thumbnail do vídeo"
    )
    
    # Versões do vídeo (armazenadas como JSON)
    versions: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Versões do vídeo em diferentes resoluções"
    )
    
    original_version: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Resolução da versão original"
    )
    
    # Controle de estado
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica se o arquivo foi deletado (soft delete)"
    )
    
    # Relacionamentos
    owner = relationship("UserModel", back_populates="video_files")
    
    def __repr__(self) -> str:
        return f"<VideoFileModel(id={self.id}, name={self.name}, owner_id={self.owner_id})>"