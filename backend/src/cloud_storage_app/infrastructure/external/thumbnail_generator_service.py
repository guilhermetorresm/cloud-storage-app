"""
Implementação concreta do serviço unificado de geração de miniaturas.
ATUALIZADO: Gera thumbnails apenas no formato JPEG padronizado.
"""
import asyncio
from typing import Tuple, Optional, Set, Dict, Any
from PIL import Image, ImageOps
import io
import xml.etree.ElementTree as ET
import re

from ...domain.services.thumbnail_generator_interface import (
    ThumbnailGeneratorService,
    ThumbnailFormat,
    ThumbnailQuality,
    ResizeMode
)


class PillowThumbnailGeneratorService(ThumbnailGeneratorService):
    """
    Implementação do serviço unificado de geração de miniaturas usando Pillow.
    PADRONIZADO: Gera thumbnails apenas no formato JPEG para consistência.
    """
    
    # Formato padrão para todos os thumbnails
    THUMBNAIL_FORMAT = ThumbnailFormat.JPEG
    
    def __init__(self):
        self._supported_formats = {
            'raster': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
            'vector': ['svg'],
            'future': []
        }
        
        self.supported_video_formats = [
            'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'
        ]
        
        # Configurações de qualidade específicas para JPEG
        self._quality_settings = {
            ThumbnailQuality.LOW: 60,
            ThumbnailQuality.MEDIUM: 75,
            ThumbnailQuality.HIGH: 90,
            ThumbnailQuality.MAXIMUM: 95
        }
    
    @property
    def supported_image_formats(self) -> list[str]:
        """Retorna todos os formatos de imagem suportados."""
        all_formats = []
        for format_group in self._supported_formats.values():
            all_formats.extend(format_group)
        return all_formats
    
    def add_supported_format(self, format_name: str, category: str = 'future'):
        """
        Adiciona suporte para um novo formato de imagem.
        
        Args:
            format_name: Nome do formato (ex: 'heif', 'avif')
            category: Categoria do formato ('raster', 'vector', 'future')
        """
        if category not in self._supported_formats:
            self._supported_formats[category] = []
        
        format_lower = format_name.lower()
        if format_lower not in self._supported_formats[category]:
            self._supported_formats[category].append(format_lower)
    
    async def is_format_supported(self, format_name: str) -> bool:
        """Verifica se um formato é suportado."""
        format_lower = format_name.lower()
        return format_lower in self.supported_image_formats
    
    async def is_vector_format(self, format_name: str) -> bool:
        """Verifica se um formato é vetorial."""
        return format_name.lower() in self._supported_formats['vector']
    
    async def detect_image_format(self, image_data: bytes) -> str:
        """
        Detecta o formato da imagem baseado no conteúdo.
        """
        # Verificar se é SVG
        if self._is_svg_data(image_data):
            return 'svg'
        
        # Para outros formatos, usar PIL
        try:
            with Image.open(io.BytesIO(image_data)) as image:
                return image.format.lower() if image.format else 'unknown'
        except Exception:
            return 'unknown'
    
    def _is_svg_data(self, data: bytes) -> bool:
        """
        Verifica se os dados representam um arquivo SVG.
        """
        try:
            text = data.decode('utf-8', errors='ignore')
            return '<svg' in text.lower() or ('<?xml' in text.lower() and '<svg' in text.lower())
        except:
            return False
    
    async def generate_image_thumbnail(
        self, 
        image_data: bytes, 
        size: Tuple[int, int] = (200, 150),
        format: ThumbnailFormat = ThumbnailFormat.JPEG,  # Ignorado - sempre JPEG
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera uma miniatura a partir de dados de imagem.
        PADRONIZADO: Sempre gera no formato JPEG independente do parâmetro format.
        """
        try:
            # Detectar formato da imagem original
            original_format = await self.detect_image_format(image_data)
            
            if original_format == 'svg':
                return await self._generate_svg_thumbnail(image_data, size, quality)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._generate_raster_thumbnail_sync, image_data, size, quality
                )
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail de imagem: {str(e)}")
    
    async def _generate_svg_thumbnail(
        self, 
        svg_data: bytes, 
        size: Tuple[int, int],
        quality: ThumbnailQuality
    ) -> bytes:
        """
        Gera thumbnail de SVG no formato JPEG.
        """
        try:
            # Criar placeholder para SVG (será substituído por renderização real no futuro)
            placeholder_image = Image.new('RGB', size, (240, 240, 240))
            
            # Adicionar indicador visual de SVG
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(placeholder_image)
                
                # Desenhar bordas
                draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(200, 200, 200), width=2)
                
                # Texto indicativo
                text = "SVG"
                bbox = draw.textbbox((0, 0), text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                
                draw.text((x, y), text, fill=(120, 120, 120))
                
            except ImportError:
                # Se não conseguir desenhar texto, usar apenas o placeholder
                pass
            
            # Salvar como JPEG
            buffer = io.BytesIO()
            placeholder_image.save(
                buffer, 
                format='JPEG',
                quality=self._quality_settings[quality],
                optimize=True,
                progressive=True
            )
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail SVG: {str(e)}")
    
    def _generate_raster_thumbnail_sync(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        quality: ThumbnailQuality
    ) -> bytes:
        """
        Geração síncrona de thumbnail para formatos raster.
        PADRONIZADO: Sempre gera JPEG.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            # Converter para RGB (necessário para JPEG)
            processed_image = self._convert_to_rgb_with_background(image)
            
            # Gerar thumbnail mantendo proporção
            processed_image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Salvar como JPEG
            buffer = io.BytesIO()
            processed_image.save(
                buffer,
                format='JPEG',
                quality=self._quality_settings[quality],
                optimize=True,
                progressive=True
            )
            buffer.seek(0)
            
            return buffer.getvalue()
    
    def _convert_to_rgb_with_background(self, image: Image.Image, bg_color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        """
        Converte imagem para RGB com fundo branco (necessário para JPEG).
        """
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, bg_color)
            if image.mode == 'P':
                image = image.convert('RGBA')
            if image.mode in ('RGBA', 'LA'):
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            return background
        elif image.mode != 'RGB':
            return image.convert('RGB')
        return image
    
    async def generate_video_thumbnail(
        self, 
        video_data: bytes, 
        timestamp: float = 0.0,
        size: Tuple[int, int] = (200, 150),
        format: ThumbnailFormat = ThumbnailFormat.JPEG,  # Ignorado - sempre JPEG
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera uma miniatura a partir de dados de vídeo.
        PADRONIZADO: Sempre gera no formato JPEG.
        
        NOTA: Esta implementação será adicionada futuramente quando
        integrarmos com bibliotecas de processamento de vídeo como FFmpeg.
        """
        raise NotImplementedError(
            "Geração de thumbnails de vídeo ainda não implementada. "
            "Esta funcionalidade será adicionada em uma versão futura."
        )
    
    async def resize_image(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        mode: ResizeMode = ResizeMode.FIT,
        format: Optional[ThumbnailFormat] = None,  # Ignorado - sempre JPEG
        quality: ThumbnailQuality = ThumbnailQuality.HIGH
    ) -> bytes:
        """
        Redimensiona uma imagem para o tamanho especificado.
        PADRONIZADO: Sempre retorna no formato JPEG.
        """
        try:
            # Detectar formato original
            original_format = await self.detect_image_format(image_data)
            
            if original_format == 'svg':
                return await self._resize_svg_image(image_data, size, mode, quality)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._resize_raster_image_sync, image_data, size, mode, quality
                )
        except Exception as e:
            raise ValueError(f"Erro ao redimensionar imagem: {str(e)}")
    
    async def _resize_svg_image(
        self, 
        svg_data: bytes, 
        size: Tuple[int, int],
        mode: ResizeMode,
        quality: ThumbnailQuality
    ) -> bytes:
        """
        Redimensiona imagem SVG e retorna como JPEG.
        """
        try:
            # Para SVG, gerar placeholder no tamanho especificado
            placeholder_image = Image.new('RGB', size, (240, 240, 240))
            
            # Adicionar indicador visual
            try:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(placeholder_image)
                draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(200, 200, 200), width=2)
                
                # Texto indicativo
                text = f"SVG {size[0]}x{size[1]}"
                bbox = draw.textbbox((0, 0), text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                
                draw.text((x, y), text, fill=(120, 120, 120))
                
            except ImportError:
                pass
            
            # Salvar como JPEG
            buffer = io.BytesIO()
            placeholder_image.save(
                buffer,
                format='JPEG',
                quality=self._quality_settings[quality],
                optimize=True,
                progressive=True
            )
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            raise ValueError(f"Erro ao redimensionar SVG: {str(e)}")
    
    def _resize_raster_image_sync(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        mode: ResizeMode,
        quality: ThumbnailQuality
    ) -> bytes:
        """
        Redimensionamento síncrono de imagem raster.
        PADRONIZADO: Sempre retorna JPEG.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            # Converter para RGB
            processed_image = self._convert_to_rgb_with_background(image)
            
            # Aplicar redimensionamento baseado no modo
            if mode == ResizeMode.FIT:
                # Manter proporção, caber dentro do tamanho
                processed_image.thumbnail(size, Image.Resampling.LANCZOS)
            elif mode == ResizeMode.FILL:
                # Manter proporção, preencher o tamanho (crop)
                processed_image = ImageOps.fit(processed_image, size, Image.Resampling.LANCZOS)
            elif mode == ResizeMode.STRETCH:
                # Forçar tamanho exato
                processed_image = processed_image.resize(size, Image.Resampling.LANCZOS)
            elif mode == ResizeMode.COVER:
                # Cobrir toda a área mantendo proporção
                processed_image = ImageOps.fit(processed_image, size, Image.Resampling.LANCZOS)
            
            # Salvar como JPEG
            buffer = io.BytesIO()
            processed_image.save(
                buffer,
                format='JPEG',
                quality=self._quality_settings[quality],
                optimize=True,
                progressive=True
            )
            buffer.seek(0)
            
            return buffer.getvalue()
    
    async def get_supported_image_formats(self) -> list[str]:
        """
        Retorna lista de formatos de imagem suportados para entrada.
        """
        return self.supported_image_formats.copy()
    
    async def get_supported_video_formats(self) -> list[str]:
        """
        Retorna lista de formatos de vídeo suportados.
        """
        return self.supported_video_formats.copy()
    
    async def get_image_info(self, image_data: bytes) -> Dict[str, Any]:
        """
        Retorna informações sobre uma imagem.
        """
        try:
            # Detectar formato
            detected_format = await self.detect_image_format(image_data)
            
            if detected_format == 'svg':
                return await self._get_svg_info(image_data)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._get_raster_info_sync, image_data, detected_format
                )
        except Exception as e:
            return {
                'format': 'unknown',
                'width': 0,
                'height': 0,
                'error': str(e)
            }
    
    async def _get_svg_info(self, svg_data: bytes) -> Dict[str, Any]:
        """
        Extrai informações de um arquivo SVG.
        """
        try:
            svg_text = svg_data.decode('utf-8')
            root = ET.fromstring(svg_text)
            
            width = self._extract_numeric_value(root.get('width', '100'))
            height = self._extract_numeric_value(root.get('height', '100'))
            
            return {
                'format': 'svg',
                'width': int(width) if width else 100,
                'height': int(height) if height else 100,
                'vector': True,
                'file_size': len(svg_data)
            }
        except Exception as e:
            return {
                'format': 'svg',
                'width': 100,
                'height': 100,
                'vector': True,
                'error': str(e)
            }
    
    def _get_raster_info_sync(self, image_data: bytes, detected_format: str) -> Dict[str, Any]:
        """
        Extrai informações de imagem raster.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            return {
                'format': detected_format,
                'width': image.size[0],
                'height': image.size[1],
                'mode': image.mode,
                'vector': False,
                'file_size': len(image_data),
                'has_transparency': image.mode in ('RGBA', 'LA', 'P')
            }
    
    def _extract_numeric_value(self, value: str) -> Optional[float]:
        """
        Extrai valor numérico de uma string, removendo unidades.
        """
        if not value or value == 'unknown':
            return None
        
        # Remover unidades comuns (px, em, %, etc.)
        numeric_match = re.match(r'^(\d+\.?\d*)', str(value))
        if numeric_match:
            try:
                return float(numeric_match.group(1))
            except ValueError:
                return None
        return None
    
    def get_thumbnail_format(self) -> ThumbnailFormat:
        """
        Retorna o formato padrão usado para thumbnails.
        """
        return self.THUMBNAIL_FORMAT
    
    def get_thumbnail_extension(self) -> str:
        """
        Retorna a extensão de arquivo para thumbnails.
        """
        return '.jpg'
    
    def get_thumbnail_mime_type(self) -> str:
        """
        Retorna o tipo MIME para thumbnails.
        """
        return 'image/jpeg'