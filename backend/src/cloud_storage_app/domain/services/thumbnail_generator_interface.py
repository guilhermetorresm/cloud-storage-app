"""
Interface para serviços de geração de miniaturas.
ATUALIZADO: Reflete a padronização para thumbnails apenas no formato JPEG.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Optional, Dict, Any, Union


class ThumbnailFormat(Enum):
    """
    Formatos suportados para entrada de imagens.
    NOTA: Thumbnails são sempre geradas em JPEG independente do formato de entrada.
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
    Níveis de qualidade para miniaturas JPEG.
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
    PADRONIZADO: Todas as thumbnails são geradas no formato JPEG para consistência.
    """
    
    @abstractmethod
    async def generate_image_thumbnail(
        self, 
        image_data: bytes, 
        size: Tuple[int, int] = (200, 150),
        format: ThumbnailFormat = ThumbnailFormat.JPEG,  # Parâmetro mantido para compatibilidade, mas ignorado
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera uma miniatura a partir de dados de imagem.
        PADRONIZADO: Sempre retorna thumbnail no formato JPEG.
        
        Args:
            image_data: Dados binários da imagem
            size: Tamanho da miniatura (largura, altura)
            format: Formato de entrada (mantido para compatibilidade, thumbnail sempre será JPEG)
            quality: Qualidade da miniatura JPEG
            
        Returns:
            Dados binários da miniatura gerada em JPEG
            
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
        format: ThumbnailFormat = ThumbnailFormat.JPEG,  # Parâmetro mantido para compatibilidade, mas ignorado
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera uma miniatura a partir de dados de vídeo.
        PADRONIZADO: Sempre retorna thumbnail no formato JPEG.
        
        Args:
            video_data: Dados binários do vídeo
            timestamp: Momento do vídeo para capturar (em segundos)
            size: Tamanho da miniatura (largura, altura)
            format: Formato de entrada (mantido para compatibilidade, thumbnail sempre será JPEG)
            quality: Qualidade da miniatura JPEG
            
        Returns:
            Dados binários da miniatura gerada em JPEG
            
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
        format: Optional[ThumbnailFormat] = None,  # Parâmetro mantido para compatibilidade, mas ignorado
        quality: ThumbnailQuality = ThumbnailQuality.HIGH
    ) -> bytes:
        """
        Redimensiona uma imagem para o tamanho especificado.
        PADRONIZADO: Sempre retorna no formato JPEG.
        
        Args:
            image_data: Dados binários da imagem
            size: Novo tamanho (largura, altura)
            mode: Modo de redimensionamento
            format: Formato de saída (mantido para compatibilidade, sempre será JPEG)
            quality: Qualidade da imagem redimensionada
            
        Returns:
            Dados binários da imagem redimensionada em JPEG
            
        Raises:
            ValueError: Se os dados da imagem são inválidos
        """
        pass
    
    @abstractmethod
    async def get_supported_image_formats(self) -> list[str]:
        """
        Retorna lista de formatos de imagem suportados para entrada.
        
        Returns:
            Lista de extensões de arquivo suportadas para entrada
        """
        pass
    
    @abstractmethod
    async def get_supported_video_formats(self) -> list[str]:
        """
        Retorna lista de formatos de vídeo suportados para entrada.
        
        Returns:
            Lista de extensões de arquivo suportadas para entrada
        """
        pass
    
    @abstractmethod
    async def is_format_supported(self, format_name: str) -> bool:
        """
        Verifica se um formato de entrada é suportado.
        
        Args:
            format_name: Nome do formato de entrada
            
        Returns:
            True se o formato é suportado para entrada
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
    
    # Novos métodos abstratos para suportar a padronização JPEG
    
    @abstractmethod
    def get_thumbnail_format(self) -> ThumbnailFormat:
        """
        Retorna o formato padrão usado para thumbnails.
        
        Returns:
            Formato padrão para thumbnails (sempre JPEG)
        """
        pass
    
    @abstractmethod
    def get_thumbnail_extension(self) -> str:
        """
        Retorna a extensão de arquivo para thumbnails.
        
        Returns:
            Extensão de arquivo para thumbnails (sempre '.jpg')
        """
        pass
    
    @abstractmethod
    def get_thumbnail_mime_type(self) -> str:
        """
        Retorna o tipo MIME para thumbnails.
        
        Returns:
            Tipo MIME para thumbnails (sempre 'image/jpeg')
        """
        pass
    
    # Métodos com implementação padrão
    
    async def generate_multi_size_thumbnails(
        self, 
        image_data: bytes,
        sizes: list[Tuple[int, int]],
        format: ThumbnailFormat = ThumbnailFormat.JPEG,  # Parâmetro mantido para compatibilidade, mas ignorado
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> Dict[Tuple[int, int], bytes]:
        """
        Gera múltiplas miniaturas em tamanhos diferentes.
        PADRONIZADO: Todas as thumbnails são geradas em JPEG.
        
        Args:
            image_data: Dados binários da imagem
            sizes: Lista de tamanhos (largura, altura)
            format: Formato de entrada (mantido para compatibilidade, thumbnails sempre serão JPEG)
            quality: Qualidade das miniaturas JPEG
            
        Returns:
            Dicionário com tamanhos como chaves e dados das miniaturas JPEG como valores
        """
        thumbnails = {}
        for size in sizes:
            try:
                # format é ignorado - sempre gera JPEG
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
        Retorna informações sobre um formato específico de entrada.
        
        Args:
            format_name: Nome do formato de entrada
            
        Returns:
            Dicionário com informações do formato
        """
        is_supported = await self.is_format_supported(format_name)
        is_vector = await self.is_vector_format(format_name)
        
        info = {
            'name': format_name,
            'supported': is_supported,
            'vector_format': is_vector,
            'category': 'vector' if is_vector else 'raster',
            'thumbnail_format': 'JPEG',  # Sempre JPEG para thumbnails
            'thumbnail_extension': '.jpg'
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
                'typical_use': 'Imagens com transparência, logos, gráficos',
                'thumbnail_note': 'Transparência será convertida para fundo branco no thumbnail JPEG'
            })
        elif format_lower == 'gif':
            info.update({
                'supports_transparency': True,
                'supports_animation': True,
                'color_limit': 256,
                'typical_use': 'Animações simples, imagens com poucas cores',
                'thumbnail_note': 'Apenas primeiro frame será usado no thumbnail JPEG'
            })
        elif format_lower == 'webp':
            info.update({
                'supports_transparency': True,
                'supports_animation': True,
                'quality_range': (1, 100),
                'modern_format': True,
                'typical_use': 'Uso geral web, boa compressão',
                'thumbnail_note': 'Transparência será convertida para fundo branco no thumbnail JPEG'
            })
        elif format_lower == 'svg':
            info.update({
                'supports_transparency': True,
                'supports_animation': True,
                'vector_format': True,
                'scalable': True,
                'typical_use': 'Logos, ícones, gráficos vetoriais',
                'thumbnail_note': 'Será rasterizado para thumbnail JPEG'
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
        PADRONIZADO: Sempre retorna apenas JPEG.
        
        Args:
            input_format: Formato da imagem de entrada
            
        Returns:
            Lista com apenas JPEG (formato padrão para thumbnails)
        """
        # Independente do formato de entrada, thumbnail sempre será JPEG
        return [ThumbnailFormat.JPEG]
    
    async def get_thumbnail_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o sistema de thumbnails.
        
        Returns:
            Dicionário com informações sobre thumbnails
        """
        return {
            'thumbnail_format': self.get_thumbnail_format().value,
            'thumbnail_extension': self.get_thumbnail_extension(),
            'thumbnail_mime_type': self.get_thumbnail_mime_type(),
            'quality_levels': {
                'LOW': ThumbnailQuality.LOW.value,
                'MEDIUM': ThumbnailQuality.MEDIUM.value,
                'HIGH': ThumbnailQuality.HIGH.value,
                'MAXIMUM': ThumbnailQuality.MAXIMUM.value
            },
            'supported_input_formats': await self.get_supported_image_formats(),
            'supported_video_formats': await self.get_supported_video_formats(),
            'standardized': True,
            'description': 'Sistema padronizado que gera thumbnails apenas em JPEG para consistência'
        }
    
    async def convert_transparency_note(self, input_format: str) -> str:
        """
        Retorna uma nota sobre como a transparência será tratada.
        
        Args:
            input_format: Formato da imagem de entrada
            
        Returns:
            Nota sobre tratamento de transparência
        """
        format_lower = input_format.lower()
        
        if format_lower in ['png', 'gif', 'webp'] or await self.is_vector_format(input_format):
            return (
                "Imagens com transparência serão convertidas para JPEG com fundo branco. "
                "A transparência será perdida no thumbnail."
            )
        elif format_lower in ['jpg', 'jpeg']:
            return "Formato JPEG não suporta transparência. Nenhuma conversão necessária."
        else:
            return "Formato será convertido para JPEG. Transparência, se presente, será perdida."