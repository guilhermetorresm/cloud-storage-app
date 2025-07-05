"""
Implementação concreta do serviço unificado de geração de miniaturas.
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
    ThumbnailQuality
)


class PillowThumbnailGeneratorService(ThumbnailGeneratorService):
    """
    Implementação corrigida do serviço unificado de geração de miniaturas usando Pillow.
    """
    
    def __init__(self):
        # CORRIGIDO: Alinhar com ImageProcessingService
        self._supported_formats = {
            'raster': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
            'vector': ['svg'],
            'future': []
        }
        
        self.supported_video_formats = [
            'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'
        ]
        
        self._quality_settings = {
            ThumbnailQuality.LOW: {'jpeg': 60, 'webp': 60},
            ThumbnailQuality.MEDIUM: {'jpeg': 75, 'webp': 75},
            ThumbnailQuality.HIGH: {'jpeg': 90, 'webp': 90},
            ThumbnailQuality.MAXIMUM: {'jpeg': 95, 'webp': 95}
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
    
    def is_format_supported(self, format_name: str) -> bool:
        """Verifica se um formato é suportado."""
        format_lower = format_name.lower()
        return format_lower in self.supported_image_formats
    
    def is_vector_format(self, format_name: str) -> bool:
        """Verifica se um formato é vetorial."""
        return format_name.lower() in self._supported_formats['vector']
    
    async def _detect_image_format(self, image_data: bytes) -> str:
        """
        Detecta o formato da imagem baseado no conteúdo.
        CORRIGIDO: Usar mesma lógica do ImageProcessingService
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
        CORRIGIDO: Usar mesma lógica do ImageProcessingService
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
        format: ThumbnailFormat = ThumbnailFormat.JPEG,
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera uma miniatura a partir de dados de imagem.
        """
        try:
            # Detectar formato da imagem original
            original_format = await self._detect_image_format(image_data)
            
            if original_format == 'svg':
                return await self._generate_svg_thumbnail(image_data, size, format, quality)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._generate_raster_thumbnail_sync, image_data, size, format, quality
                )
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail de imagem: {str(e)}")
    
    async def _generate_svg_thumbnail(
        self, 
        svg_data: bytes, 
        size: Tuple[int, int],
        format: ThumbnailFormat,
        quality: ThumbnailQuality
    ) -> bytes:
        """
        Gera thumbnail de SVG.
        CORRIGIDO: Usar mesma abordagem do ImageProcessingService
        """
        try:
            # Criar placeholder consistente
            placeholder_image = Image.new('RGB', size, (240, 240, 240))
            
            # Salvar com o formato especificado
            buffer = io.BytesIO()
            save_kwargs = self._get_save_kwargs(format, quality)
            placeholder_image.save(buffer, **save_kwargs)
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail SVG: {str(e)}")
    
    def _generate_raster_thumbnail_sync(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        format: ThumbnailFormat,
        quality: ThumbnailQuality
    ) -> bytes:
        """
        Geração síncrona de thumbnail para formatos raster.
        CORRIGIDO: Melhor tratamento de formatos e consistência
        """
        with Image.open(io.BytesIO(image_data)) as image:
            # Preparar a imagem baseada no formato de saída
            processed_image = self._prepare_image_for_format(image, format)
            
            # Gerar thumbnail mantendo proporção
            processed_image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Salvar com as configurações especificadas
            buffer = io.BytesIO()
            save_kwargs = self._get_save_kwargs(format, quality)
            processed_image.save(buffer, **save_kwargs)
            buffer.seek(0)
            
            return buffer.getvalue()
    
    def _prepare_image_for_format(self, image: Image.Image, format: ThumbnailFormat) -> Image.Image:
        """
        Prepara a imagem para o formato de saída especificado.
        CORRIGIDO: Usar mesma lógica de conversão do ImageProcessingService
        """
        if format == ThumbnailFormat.JPEG:
            return self._convert_to_rgb_with_background(image)
        elif format == ThumbnailFormat.PNG:
            return self._prepare_for_transparency_format(image)
        elif format == ThumbnailFormat.WEBP:
            return self._prepare_for_transparency_format(image)
        elif format == ThumbnailFormat.GIF:
            return self._prepare_for_gif(image)
        
        return image
    
    def _convert_to_rgb_with_background(self, image: Image.Image, bg_color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        """
        Converte imagem para RGB com fundo especificado.
        CORRIGIDO: Usar mesma lógica do ImageProcessingService
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
    
    def _prepare_for_transparency_format(self, image: Image.Image) -> Image.Image:
        """Prepara imagem para formatos que suportam transparência."""
        if image.mode == 'P':
            return image.convert('RGBA')
        elif image.mode not in ('RGB', 'RGBA'):
            return image.convert('RGBA')
        return image
    
    def _prepare_for_gif(self, image: Image.Image) -> Image.Image:
        """Prepara imagem para formato GIF."""
        if image.mode not in ('P', 'RGB'):
            if image.mode == 'RGBA':
                return image.convert('P', palette=Image.ADAPTIVE, colors=255)
            else:
                return image.convert('RGB')
        return image
    
    def _get_save_kwargs(self, format: ThumbnailFormat, quality: ThumbnailQuality) -> dict:
        """
        Obtém argumentos de salvamento baseados no formato e qualidade.
        CORRIGIDO: Melhor tratamento de parâmetros
        """
        base_kwargs = {
            'format': format.value,
            'optimize': True
        }
        
        if format == ThumbnailFormat.JPEG:
            base_kwargs['quality'] = self._quality_settings[quality]['jpeg']
            base_kwargs['progressive'] = True
        elif format == ThumbnailFormat.PNG:
            compression_levels = {
                ThumbnailQuality.LOW: 1,
                ThumbnailQuality.MEDIUM: 6,
                ThumbnailQuality.HIGH: 9,
                ThumbnailQuality.MAXIMUM: 9
            }
            base_kwargs['compress_level'] = compression_levels[quality]
        elif format == ThumbnailFormat.WEBP:
            base_kwargs['quality'] = self._quality_settings[quality]['webp']
            base_kwargs['method'] = 6
        elif format == ThumbnailFormat.GIF:
            base_kwargs['save_all'] = True
            base_kwargs['optimize'] = True
        
        return base_kwargs
    
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
        maintain_aspect_ratio: bool = True,
        format: Optional[ThumbnailFormat] = None
    ) -> bytes:
        """
        Redimensiona uma imagem para o tamanho especificado.
        """
        try:
            # Detectar formato original
            original_format = await self._detect_image_format(image_data)
            
            if original_format == 'svg':
                return await self._resize_svg_image(image_data, size, maintain_aspect_ratio, format)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._resize_raster_image_sync, image_data, size, maintain_aspect_ratio, format, original_format
                )
        except Exception as e:
            raise ValueError(f"Erro ao redimensionar imagem: {str(e)}")
    
    async def _resize_svg_image(
        self, 
        svg_data: bytes, 
        size: Tuple[int, int],
        maintain_aspect_ratio: bool,
        format: Optional[ThumbnailFormat]
    ) -> bytes:
        """
        Redimensiona imagem SVG.
        """
        try:
            # Para SVG, modificar os atributos width/height no XML
            svg_text = svg_data.decode('utf-8')
            root = ET.fromstring(svg_text)
            
            if maintain_aspect_ratio:
                # Calcular proporção baseada no viewBox ou dimensões existentes
                original_width = self._extract_numeric_value(root.get('width', '100'))
                original_height = self._extract_numeric_value(root.get('height', '100'))
                
                if original_width and original_height:
                    aspect_ratio = original_width / original_height
                    new_width, new_height = self._calculate_aspect_ratio_size(size, aspect_ratio)
                else:
                    new_width, new_height = size
            else:
                new_width, new_height = size
            
            # Atualizar dimensões no SVG
            root.set('width', str(new_width))
            root.set('height', str(new_height))
            
            # Converter de volta para bytes
            modified_svg = ET.tostring(root, encoding='utf-8')
            
            # Se formato específico foi solicitado e não é SVG, converter
            if format and format != ThumbnailFormat.SVG:
                # Aqui seria necessário converter SVG para raster
                # Por enquanto, retornar placeholder
                return await self._generate_svg_thumbnail(modified_svg, (new_width, new_height), format, ThumbnailQuality.HIGH)
            
            return modified_svg
            
        except Exception as e:
            raise ValueError(f"Erro ao redimensionar SVG: {str(e)}")
    
    def _extract_numeric_value(self, value: str) -> Optional[float]:
        """
        Extrai valor numérico de uma string, removendo unidades.
        CORRIGIDO: Usar mesma implementação do ImageProcessingService
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
    
    def _calculate_aspect_ratio_size(self, target_size: Tuple[int, int], aspect_ratio: float) -> Tuple[int, int]:
        """
        Calcula novo tamanho mantendo proporção.
        """
        target_width, target_height = target_size
        
        # Calcular baseado na largura
        new_height = int(target_width / aspect_ratio)
        if new_height <= target_height:
            return (target_width, new_height)
        
        # Calcular baseado na altura
        new_width = int(target_height * aspect_ratio)
        return (new_width, target_height)
    
    def _resize_raster_image_sync(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        maintain_aspect_ratio: bool,
        format: Optional[ThumbnailFormat],
        original_format: str
    ) -> bytes:
        """
        Redimensionamento síncrono de imagem raster.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            if maintain_aspect_ratio:
                # Usar thumbnail para manter proporção
                image.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                # Redimensionar forçadamente para o tamanho exato
                image = image.resize(size, Image.Resampling.LANCZOS)
            
            # Determinar formato de saída
            if format is not None:
                output_format = format
                image = self._prepare_image_for_format(image, format)
                save_kwargs = self._get_save_kwargs(format, ThumbnailQuality.HIGH)
            else:
                # Manter formato original se possível
                output_format = self._get_thumbnail_format_from_string(original_format)
                if output_format:
                    image = self._prepare_image_for_format(image, output_format)
                    save_kwargs = self._get_save_kwargs(output_format, ThumbnailQuality.HIGH)
                else:
                    # Fallback para JPEG
                    output_format = ThumbnailFormat.JPEG
                    image = self._prepare_image_for_format(image, output_format)
                    save_kwargs = self._get_save_kwargs(output_format, ThumbnailQuality.HIGH)
            
            # Salvar resultado
            buffer = io.BytesIO()
            image.save(buffer, **save_kwargs)
            buffer.seek(0)
            
            return buffer.getvalue()
    
    def _get_thumbnail_format_from_string(self, format_string: str) -> Optional[ThumbnailFormat]:
        """
        Converte string de formato para ThumbnailFormat.
        """
        format_mapping = {
            'jpeg': ThumbnailFormat.JPEG,
            'jpg': ThumbnailFormat.JPEG,
            'png': ThumbnailFormat.PNG,
            'webp': ThumbnailFormat.WEBP,
            'gif': ThumbnailFormat.GIF
        }
        return format_mapping.get(format_string.lower())
    
    async def generate_multi_size_thumbnails(
        self, 
        image_data: bytes,
        sizes: list[Tuple[int, int]],
        format: ThumbnailFormat = ThumbnailFormat.JPEG,
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> Dict[Tuple[int, int], bytes]:
        """
        Gera múltiplas miniaturas em tamanhos diferentes.
        """
        thumbnails = {}
        
        for size in sizes:
            try:
                thumbnail = await self.generate_image_thumbnail(image_data, size, format, quality)
                thumbnails[size] = thumbnail
            except Exception as e:
                # Log do erro, mas continua com outros tamanhos
                print(f"Erro ao gerar thumbnail {size}: {str(e)}")
                continue
        
        return thumbnails
    
    async def get_optimal_thumbnail_size(
        self, 
        image_data: bytes, 
        max_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        Calcula o tamanho ótimo para thumbnail baseado na imagem original.
        """
        try:
            # Detectar formato
            original_format = await self._detect_image_format(image_data)
            
            if original_format == 'svg':
                # Para SVG, usar tamanho máximo
                return max_size
            else:
                # Para raster, calcular baseado nas dimensões originais
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._get_optimal_size_sync, image_data, max_size
                )
        except Exception:
            return max_size
    
    def _get_optimal_size_sync(self, image_data: bytes, max_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calcula tamanho ótimo de forma síncrona.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            original_width, original_height = image.size
            max_width, max_height = max_size
            
            # Se a imagem já é menor que o máximo, manter tamanho original
            if original_width <= max_width and original_height <= max_height:
                return (original_width, original_height)
            
            # Calcular proporção
            aspect_ratio = original_width / original_height
            
            # Calcular novo tamanho mantendo proporção
            if aspect_ratio > 1:  # Landscape
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
                if new_height > max_height:
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
            else:  # Portrait ou quadrado
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
                if new_width > max_width:
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
            
            return (new_width, new_height)
    
    async def get_supported_image_formats(self) -> list[str]:
        """
        Retorna lista de formatos de imagem suportados.
        """
        return self.supported_image_formats.copy()
    
    async def get_supported_video_formats(self) -> list[str]:
        """
        Retorna lista de formatos de vídeo suportados.
        """
        return self.supported_video_formats.copy()
    
    async def get_format_info(self, format_name: str) -> Dict[str, Any]:
        """
        Retorna informações sobre um formato específico.
        """
        format_lower = format_name.lower()
        
        info = {
            'name': format_name,
            'supported': format_lower in self.supported_image_formats,
            'category': 'unknown'
        }
        
        # Determinar categoria
        for category, formats in self._supported_formats.items():
            if format_lower in formats:
                info['category'] = category
                break
        
        # Adicionar informações específicas
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