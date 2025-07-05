"""
Interface para serviços de geração de miniaturas.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Optional, Dict, Any


class ThumbnailFormat(Enum):
    """
    Formatos suportados para miniaturas.
    """
    JPEG = "JPEG"
    PNG = "PNG"
    GIF = "GIF"
    WEBP = "WEBP"
    SVG = "SVG"
    
    # Formatos futuros podem ser adicionados aqui
    # HEIF = "HEIF"
    # AVIF = "AVIF"
    # JXL = "JXL"  # JPEG XL


class ThumbnailQuality(Enum):
    """
    Níveis de qualidade para miniaturas.
    """
    LOW = 60
    MEDIUM = 75
    HIGH = 90
    MAXIMUM = 95


class ThumbnailGeneratorService(ABC):
    """
    Interface para serviços de geração de miniaturas unificadas.
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
            image_data: Dados binários da imagem
            size: Tamanho da miniatura (largura, altura)
            format: Formato de saída da miniatura
            quality: Qualidade da miniatura
            
        Returns:
            Dados binários da miniatura gerada
            
        Raises:
            ValueError: Se os dados da imagem são inválidos
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
            video_data: Dados binários do vídeo
            timestamp: Momento do vídeo para capturar (em segundos)
            size: Tamanho da miniatura (largura, altura)
            format: Formato de saída da miniatura
            quality: Qualidade da miniatura
            
        Returns:
            Dados binários da miniatura gerada
            
        Raises:
            ValueError: Se os dados do vídeo são inválidos
            NotImplementedError: Se não há suporte para vídeo
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
            image_data: Dados binários da imagem
            size: Novo tamanho (largura, altura)
            maintain_aspect_ratio: Se deve manter a proporção
            format: Formato de saída (None para manter o original)
            
        Returns:
            Dados binários da imagem redimensionada
            
        Raises:
            ValueError: Se os dados da imagem são inválidos
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
    
    # Métodos adicionais para funcionalidades estendidas
    
    async def generate_multi_size_thumbnails(
        self, 
        image_data: bytes,
        sizes: list[Tuple[int, int]],
        format: ThumbnailFormat = ThumbnailFormat.JPEG,
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> Dict[Tuple[int, int], bytes]:
        """
        Gera múltiplas miniaturas em tamanhos diferentes.
        
        Args:
            image_data: Dados binários da imagem
            sizes: Lista de tamanhos (largura, altura)
            format: Formato de saída das miniaturas
            quality: Qualidade das miniaturas
            
        Returns:
            Dicionário com tamanhos como chaves e dados das miniaturas como valores
        """
        thumbnails = {}
        for size in sizes:
            try:
                thumbnail = await self.generate_image_thumbnail(image_data, size, format, quality)
                thumbnails[size] = thumbnail
            except Exception:
                # Continuar com outros tamanhos em caso de erro
                continue
        return thumbnails
    
    async def get_optimal_thumbnail_size(
        self, 
        image_data: bytes, 
        max_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        Calcula o tamanho ótimo para thumbnail baseado na imagem original.
        
        Args:
            image_data: Dados binários da imagem
            max_size: Tamanho máximo permitido
            
        Returns:
            Tamanho ótimo calculado
        """
        # Implementação padrão - subclasses podem sobrescrever
        return max_size
    
    async def get_format_info(self, format_name: str) -> Dict[str, Any]:
        """
        Retorna informações sobre um formato específico.
        
        Args:
            format_name: Nome do formato
            
        Returns:
            Dicionário com informações do formato
        """
        # Implementação padrão - subclasses podem sobrescrever
        return {
            'name': format_name,
            'supported': format_name.lower() in await self.get_supported_image_formats()
        }
    
    def is_format_supported(self, format_name: str) -> bool:
        """
        Verifica se um formato é suportado.
        
        Args:
            format_name: Nome do formato
            
        Returns:
            True se o formato é suportado
        """
        # Implementação padrão - subclasses podem sobrescrever
        return False
    
    def is_vector_format(self, format_name: str) -> bool:
        """
        Verifica se um formato é vetorial.
        
        Args:
            format_name: Nome do formato
            
        Returns:
            True se o formato é vetorial
        """
        # Implementação padrão - subclasses podem sobrescrever
        return format_name.upper() == 'SVG'