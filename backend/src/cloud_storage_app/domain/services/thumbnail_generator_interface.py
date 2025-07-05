"""
Interface para serviços de geração de miniaturas.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Optional, Dict, Any, Union


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


class ResizeMode(Enum):
    """
    Modos de redimensionamento de imagem.
    """
    FIT = "fit"  # Mantém proporção, cabe dentro do tamanho
    FILL = "fill"  # Mantém proporção, preenche o tamanho (crop)
    STRETCH = "stretch"  # Força tamanho exato, pode distorcer
    COVER = "cover"  # Mantém proporção, cobre toda a área


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
        mode: ResizeMode = ResizeMode.FIT,
        format: Optional[ThumbnailFormat] = None,
        quality: ThumbnailQuality = ThumbnailQuality.HIGH
    ) -> bytes:
        """
        Redimensiona uma imagem para o tamanho especificado.
        
        Args:
            image_data: Dados binários da imagem
            size: Novo tamanho (largura, altura)
            mode: Modo de redimensionamento
            format: Formato de saída (None para manter o original)
            quality: Qualidade da imagem redimensionada
            
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
    
    @abstractmethod
    async def is_format_supported(self, format_name: str) -> bool:
        """
        Verifica se um formato é suportado.
        
        Args:
            format_name: Nome do formato
            
        Returns:
            True se o formato é suportado
        """
        pass
    
    @abstractmethod
    async def is_vector_format(self, format_name: str) -> bool:
        """
        Verifica se um formato é vetorial.
        
        Args:
            format_name: Nome do formato
            
        Returns:
            True se o formato é vetorial
        """
        pass
    
    @abstractmethod
    async def detect_image_format(self, image_data: bytes) -> str:
        """
        Detecta o formato de uma imagem baseado no conteúdo.
        
        Args:
            image_data: Dados binários da imagem
            
        Returns:
            Nome do formato detectado
        """
        pass
    
    @abstractmethod
    async def get_image_info(self, image_data: bytes) -> Dict[str, Any]:
        """
        Retorna informações sobre uma imagem.
        
        Args:
            image_data: Dados binários da imagem
            
        Returns:
            Dicionário com informações da imagem (dimensões, formato, etc.)
        """
        pass
    
    # Métodos com implementação padrão
    
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
        try:
            image_info = await self.get_image_info(image_data)
            original_width = image_info.get('width', max_size[0])
            original_height = image_info.get('height', max_size[1])
            
            # Se a imagem já é menor que o máximo, manter tamanho original
            if original_width <= max_size[0] and original_height <= max_size[1]:
                return (original_width, original_height)
            
            # Calcular proporção
            aspect_ratio = original_width / original_height
            
            # Calcular novo tamanho mantendo proporção
            if aspect_ratio > 1:  # Landscape
                new_width = max_size[0]
                new_height = int(max_size[0] / aspect_ratio)
                if new_height > max_size[1]:
                    new_height = max_size[1]
                    new_width = int(max_size[1] * aspect_ratio)
            else:  # Portrait ou quadrado
                new_height = max_size[1]
                new_width = int(max_size[1] * aspect_ratio)
                if new_width > max_size[0]:
                    new_width = max_size[0]
                    new_height = int(max_size[0] / aspect_ratio)
            
            return (new_width, new_height)
        except Exception:
            return max_size
    
    async def get_format_info(self, format_name: str) -> Dict[str, Any]:
        """
        Retorna informações sobre um formato específico.
        
        Args:
            format_name: Nome do formato
            
        Returns:
            Dicionário com informações do formato
        """
        is_supported = await self.is_format_supported(format_name)
        is_vector = await self.is_vector_format(format_name)
        
        info = {
            'name': format_name,
            'supported': is_supported,
            'vector_format': is_vector,
            'category': 'vector' if is_vector else 'raster'
        }
        
        # Adicionar informações específicas por formato
        format_lower = format_name.lower()
        if format_lower in ['jpg', 'jpeg']:
            info.update({
                'supports_transparency': False,
                'supports_animation': False,
                'quality_range': (1, 100),
                'typical_use': 'Fotografias e imagens com muitas cores'
            })
        elif format_lower == 'png':
            info.update({
                'supports_transparency': True,
                'supports_animation': False,
                'lossless': True,
                'typical_use': 'Imagens com transparência, logos, gráficos'
            })
        elif format_lower == 'gif':
            info.update({
                'supports_transparency': True,
                'supports_animation': True,
                'color_limit': 256,
                'typical_use': 'Animações simples, imagens com poucas cores'
            })
        elif format_lower == 'webp':
            info.update({
                'supports_transparency': True,
                'supports_animation': True,
                'quality_range': (1, 100),
                'modern_format': True,
                'typical_use': 'Uso geral web, boa compressão'
            })
        elif format_lower == 'svg':
            info.update({
                'supports_transparency': True,
                'supports_animation': True,
                'vector_format': True,
                'scalable': True,
                'typical_use': 'Logos, ícones, gráficos vetoriais'
            })
        
        return info
    
    async def validate_image_data(self, image_data: bytes) -> bool:
        """
        Valida se os dados representam uma imagem válida.
        
        Args:
            image_data: Dados binários a serem validados
            
        Returns:
            True se os dados são válidos
        """
        try:
            format_name = await self.detect_image_format(image_data)
            return format_name != 'unknown' and await self.is_format_supported(format_name)
        except Exception:
            return False
    
    async def get_thumbnail_formats_for_input(self, input_format: str) -> list[ThumbnailFormat]:
        """
        Retorna os formatos de thumbnail recomendados para um formato de entrada.
        
        Args:
            input_format: Formato da imagem de entrada
            
        Returns:
            Lista de formatos recomendados para thumbnail
        """
        if await self.is_vector_format(input_format):
            return [ThumbnailFormat.PNG, ThumbnailFormat.WEBP, ThumbnailFormat.SVG]
        else:
            return [ThumbnailFormat.JPEG, ThumbnailFormat.WEBP, ThumbnailFormat.PNG]