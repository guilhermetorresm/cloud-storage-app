from abc import ABC, abstractmethod
from typing import Tuple, Optional
from enum import Enum


class ThumbnailFormat(Enum):
    """Formatos suportados para thumbnails"""
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"


class ThumbnailQuality(Enum):
    """Níveis de qualidade para thumbnails"""
    LOW = 60
    MEDIUM = 80
    HIGH = 95


class ThumbnailGeneratorService(ABC):
    """
    Interface para serviço unificado de geração de miniaturas.
    
    Este serviço será usado tanto para imagens quanto para vídeos,
    fornecendo uma interface comum para geração de thumbnails.
    """
    
    @abstractmethod
    async def generate_image_thumbnail(
        self, 
        image_data: bytes, 
        size: Tuple[int, int] = (200, 150),
        format: ThumbnailFormat = ThumbnailFormat.JPEG,
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera uma miniatura a partir de dados de imagem.
        
        Args:
            image_data: Dados binários da imagem original
            size: Tupla com largura e altura da miniatura
            format: Formato da miniatura (JPEG, PNG, WEBP)
            quality: Qualidade da miniatura
            
        Returns:
            Dados binários da miniatura gerada
        """
        pass
    
    @abstractmethod
    async def generate_video_thumbnail(
        self, 
        video_data: bytes, 
        timestamp: float = 0.0,
        size: Tuple[int, int] = (200, 150),
        format: ThumbnailFormat = ThumbnailFormat.JPEG,
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera uma miniatura a partir de dados de vídeo.
        
        Args:
            video_data: Dados binários do vídeo original
            timestamp: Tempo em segundos para extrair o frame
            size: Tupla com largura e altura da miniatura
            format: Formato da miniatura (JPEG, PNG, WEBP)
            quality: Qualidade da miniatura
            
        Returns:
            Dados binários da miniatura gerada
        """
        pass
    
    @abstractmethod
    async def resize_image(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        maintain_aspect_ratio: bool = True,
        format: Optional[ThumbnailFormat] = None
    ) -> bytes:
        """
        Redimensiona uma imagem para o tamanho especificado.
        
        Args:
            image_data: Dados binários da imagem original
            size: Tupla com largura e altura desejadas
            maintain_aspect_ratio: Se deve manter a proporção da imagem
            format: Formato de saída (se None, mantém o formato original)
            
        Returns:
            Dados binários da imagem redimensionada
        """
        pass
    
    @abstractmethod
    async def get_supported_image_formats(self) -> list[str]:
        """
        Retorna lista de formatos de imagem suportados.
        
        Returns:
            Lista de extensões de arquivo suportadas
        """
        pass
    
    @abstractmethod
    async def get_supported_video_formats(self) -> list[str]:
        """
        Retorna lista de formatos de vídeo suportados.
        
        Returns:
            Lista de extensões de arquivo suportadas
        """
        pass