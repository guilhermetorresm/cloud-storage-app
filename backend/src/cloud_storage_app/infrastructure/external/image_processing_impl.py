"""
Implementação concreta do serviço de processamento de imagens.
"""
import asyncio
from typing import Dict, Any, Tuple, Set, Optional
from datetime import datetime
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import io
import os
import mimetypes
import xml.etree.ElementTree as ET
import re

from ...domain.services.image_processing_interface import ImageProcessingService


class PillowImageProcessingService(ImageProcessingService):
    """
    Implementação do serviço de processamento de imagens usando Pillow (PIL).
    Suporta: JPEG, PNG, GIF, SVG, WebP com extensibilidade para novos formatos.
    """
    
    def __init__(self):
        # Formatos de imagem suportados organizados por tipo
        self._supported_formats = {
            # Formatos raster (bitmap)
            'raster': {'JPEG', 'JPG', 'PNG', 'GIF', 'WEBP'},
            # Formatos vetoriais
            'vector': {'SVG'},
            # Formatos especiais/futuros podem ser adicionados aqui
            'special': set()
        }
        
        # Mapeamento de extensões para tipos MIME
        self._mime_types = {
            'jpeg': 'image/jpeg',
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml'
        }
        
        # Configurações específicas por formato
        self._format_config = {
            'JPEG': {'quality_range': (1, 100), 'supports_transparency': False},
            'PNG': {'compression_range': (0, 9), 'supports_transparency': True},
            'GIF': {'supports_animation': True, 'supports_transparency': True},
            'WEBP': {'quality_range': (1, 100), 'supports_transparency': True, 'supports_animation': True},
            'SVG': {'is_vector': True, 'supports_transparency': True}
        }
    
    @property
    def supported_formats(self) -> Set[str]:
        """Retorna todos os formatos suportados."""
        all_formats = set()
        for format_group in self._supported_formats.values():
            all_formats.update(format_group)
        return all_formats
    
    def add_supported_format(self, format_name: str, format_type: str = 'special', 
                           mime_type: Optional[str] = None, config: Optional[Dict] = None):
        """
        Adiciona suporte para um novo formato de imagem.
        
        Args:
            format_name: Nome do formato (ex: 'HEIF', 'AVIF')
            format_type: Tipo do formato ('raster', 'vector', 'special')
            mime_type: Tipo MIME opcional
            config: Configurações específicas do formato
        """
        if format_type not in self._supported_formats:
            self._supported_formats[format_type] = set()
        
        self._supported_formats[format_type].add(format_name.upper())
        
        if mime_type:
            self._mime_types[format_name.lower()] = mime_type
        
        if config:
            self._format_config[format_name.upper()] = config
    
    def is_format_supported(self, format_name: str) -> bool:
        """Verifica se um formato é suportado."""
        return format_name.upper() in self.supported_formats
    
    def is_vector_format(self, format_name: str) -> bool:
        """Verifica se um formato é vetorial."""
        return format_name.upper() in self._supported_formats['vector']
    
    async def extract_metadata(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extrai metadados completos de uma imagem.
        """
        try:
            # Determinar formato baseado no conteúdo e extensão
            format_info = await self._detect_format(image_data, filename)
            
            if format_info['format'] == 'SVG':
                return await self._extract_svg_metadata(image_data, filename)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._extract_raster_metadata_sync, image_data, filename, format_info
                )
        except Exception as e:
            raise ValueError(f"Erro ao extrair metadados da imagem: {str(e)}")
    
    async def _detect_format(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Detecta o formato da imagem baseado no conteúdo e extensão.
        """
        # Verificar se é SVG primeiro
        if self._is_svg_data(image_data):
            return {
                'format': 'SVG',
                'is_vector': True,
                'mime_type': 'image/svg+xml'
            }
        
        # Para formatos raster, usar PIL
        try:
            with Image.open(io.BytesIO(image_data)) as image:
                format_name = image.format
                return {
                    'format': format_name,
                    'is_vector': False,
                    'mime_type': self._get_mime_type(format_name, filename)
                }
        except Exception:
            # Fallback para extensão do arquivo
            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if ext in self._mime_types:
                return {
                    'format': ext.upper(),
                    'is_vector': ext.upper() in self._supported_formats['vector'],
                    'mime_type': self._mime_types[ext]
                }
            raise ValueError(f"Formato de imagem não suportado: {filename}")
    
    def _is_svg_data(self, data: bytes) -> bool:
        """
        Verifica se os dados representam um arquivo SVG.
        """
        try:
            # Tentar decodificar como texto
            text = data.decode('utf-8', errors='ignore')
            # Verificar se contém elementos SVG
            return '<svg' in text.lower() or '<?xml' in text.lower()
        except:
            return False
    
    def _get_mime_type(self, format_name: str, filename: str) -> str:
        """
        Obtém o tipo MIME baseado no formato e nome do arquivo.
        """
        if format_name:
            format_lower = format_name.lower()
            if format_lower in self._mime_types:
                return self._mime_types[format_lower]
        
        # Fallback usando mimetypes
        mime_type = mimetypes.guess_type(filename)[0]
        if mime_type:
            return mime_type
        
        # Fallback final
        return f"image/{format_name.lower()}" if format_name else "image/unknown"
    
    async def _extract_svg_metadata(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extrai metadados específicos de arquivos SVG.
        """
        try:
            svg_text = image_data.decode('utf-8')
            root = ET.fromstring(svg_text)
            
            # Extrair dimensões
            width = root.get('width', 'unknown')
            height = root.get('height', 'unknown')
            viewbox = root.get('viewBox', '')
            
            # Tentar extrair dimensões numéricas
            numeric_width = self._extract_numeric_value(width)
            numeric_height = self._extract_numeric_value(height)
            
            # Se não há dimensões explícitas, tentar viewBox
            if not numeric_width or not numeric_height:
                if viewbox:
                    try:
                        vb_parts = viewbox.split()
                        if len(vb_parts) >= 4:
                            numeric_width = float(vb_parts[2])
                            numeric_height = float(vb_parts[3])
                    except (ValueError, IndexError):
                        pass
            
            metadata = {
                # Propriedades do arquivo
                'filename': filename,
                'file_size': len(image_data),
                'upload_date': datetime.utcnow().isoformat(),
                'mime_type': 'image/svg+xml',
                
                # Propriedades da imagem
                'dimensions': {
                    'width': numeric_width or 'unknown',
                    'height': numeric_height or 'unknown',
                    'width_original': width,
                    'height_original': height,
                    'viewbox': viewbox
                },
                'color_depth': 'vector',
                'color_mode': 'vector',
                'format': 'SVG',
                'resolution': {'dpi_x': 'vector', 'dpi_y': 'vector'},
                
                # Dados específicos do SVG
                'svg_info': {
                    'namespace': root.tag if '}' in root.tag else None,
                    'elements_count': len(list(root.iter())),
                    'has_text': bool(list(root.iter('{http://www.w3.org/2000/svg}text'))),
                    'has_images': bool(list(root.iter('{http://www.w3.org/2000/svg}image'))),
                    'has_animations': bool(list(root.iter('{http://www.w3.org/2000/svg}animate')) or 
                                          list(root.iter('{http://www.w3.org/2000/svg}animateTransform')))
                },
                
                # Dados EXIF (não aplicável para SVG)
                'exif': {},
                
                # Informações adicionais
                'has_transparency': True,  # SVG sempre suporta transparência
                'is_animated': bool(list(root.iter('{http://www.w3.org/2000/svg}animate')) or 
                                  list(root.iter('{http://www.w3.org/2000/svg}animateTransform'))),
                'frame_count': 1,
                'is_vector': True
            }
            
            return metadata
            
        except Exception as e:
            raise ValueError(f"Erro ao processar SVG: {str(e)}")
    
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
    
    def _extract_raster_metadata_sync(self, image_data: bytes, filename: str, format_info: Dict) -> Dict[str, Any]:
        """
        Extração síncrona de metadados para formatos raster.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            # Metadados básicos do arquivo
            file_size = len(image_data)
            mime_type = format_info['mime_type']
            
            # Propriedades da imagem
            width, height = image.size
            mode = image.mode
            format_name = image.format
            
            # Calcular profundidade de cor
            color_depth = self._calculate_color_depth(mode)
            
            # Obter informações de DPI se disponível
            dpi = image.info.get('dpi', (72, 72))
            
            # Extrair dados EXIF
            exif_data = self._extract_exif_sync(image)
            
            # Verificar se é animado (para GIF e WebP)
            is_animated = getattr(image, 'is_animated', False)
            frame_count = getattr(image, 'n_frames', 1)
            
            metadata = {
                # Propriedades do arquivo
                'filename': filename,
                'file_size': file_size,
                'upload_date': datetime.utcnow().isoformat(),
                'mime_type': mime_type,
                
                # Propriedades da imagem
                'dimensions': {
                    'width': width,
                    'height': height
                },
                'color_depth': color_depth,
                'color_mode': mode,
                'format': format_name,
                'resolution': {
                    'dpi_x': dpi[0] if isinstance(dpi, tuple) else dpi,
                    'dpi_y': dpi[1] if isinstance(dpi, tuple) else dpi
                },
                
                # Dados EXIF
                'exif': exif_data,
                
                # Informações adicionais
                'has_transparency': self._has_transparency(image),
                'is_animated': is_animated,
                'frame_count': frame_count,
                'is_vector': False,
                
                # Informações específicas do formato
                'format_info': self._get_format_specific_info(format_name, image)
            }
            
            return metadata
    
    def _has_transparency(self, image: Image.Image) -> bool:
        """
        Verifica se a imagem tem transparência.
        """
        return (
            'transparency' in image.info or
            image.mode in ('RGBA', 'LA') or
            (image.mode == 'P' and 'transparency' in image.info)
        )
    
    def _get_format_specific_info(self, format_name: str, image: Image.Image) -> Dict[str, Any]:
        """
        Obtém informações específicas do formato.
        """
        info = {}
        
        if format_name in self._format_config:
            config = self._format_config[format_name]
            
            # Adicionar informações de configuração
            for key, value in config.items():
                if key.startswith('supports_'):
                    info[key] = value
        
        # Informações específicas do PIL
        if hasattr(image, 'info'):
            if format_name == 'PNG':
                info['compression'] = image.info.get('compression', 'unknown')
            elif format_name == 'JPEG':
                info['quality'] = image.info.get('quality', 'unknown')
            elif format_name in ('GIF', 'WEBP'):
                info['loop_count'] = image.info.get('loop', 0)
        
        return info
    
    def _calculate_color_depth(self, mode: str) -> int:
        """
        Calcula a profundidade de cor baseada no modo da imagem.
        """
        mode_depths = {
            '1': 1,      # Bitmap
            'L': 8,      # Grayscale
            'P': 8,      # Palette
            'RGB': 24,   # True Color
            'RGBA': 32,  # True Color + Alpha
            'CMYK': 32,  # CMYK
            'YCbCr': 24, # YCbCr
            'LAB': 24,   # LAB
            'HSV': 24,   # HSV
        }
        return mode_depths.get(mode, 24)
    
    def _extract_exif_sync(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extrai dados EXIF de forma síncrona.
        """
        exif_data = {}
        
        try:
            if hasattr(image, '_getexif') and image._getexif() is not None:
                exif_dict = image._getexif()
                
                for tag_id, value in exif_dict.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Converter valores para tipos serializáveis
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except UnicodeDecodeError:
                            value = str(value)
                    elif isinstance(value, tuple):
                        value = list(value)
                    
                    exif_data[tag] = value
                    
        except Exception:
            # Se não conseguir extrair EXIF, retorna dict vazio
            pass
        
        return exif_data
    
    async def generate_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (200, 150)) -> bytes:
        """
        Gera uma miniatura da imagem.
        """
        try:
            format_info = await self._detect_format(image_data, "")
            
            if format_info['format'] == 'SVG':
                return await self._generate_svg_thumbnail(image_data, size)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._generate_raster_thumbnail_sync, image_data, size
                )
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail: {str(e)}")
    
    async def _generate_svg_thumbnail(self, svg_data: bytes, size: Tuple[int, int]) -> bytes:
        """
        Gera thumbnail de SVG convertendo para PNG.
        """
        try:
            # Para SVG, precisaríamos de uma biblioteca como cairosvg
            # Por enquanto, retornar um placeholder ou erro
            raise NotImplementedError(
                "Geração de thumbnail para SVG requer biblioteca adicional (cairosvg). "
                "Considere converter o SVG para PNG primeiro."
            )
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail SVG: {str(e)}")
    
    def _generate_raster_thumbnail_sync(self, image_data: bytes, size: Tuple[int, int]) -> bytes:
        """
        Geração síncrona de thumbnail para formatos raster.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            # Converter para RGB se necessário (para compatibilidade com JPEG)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if image.mode in ('RGBA', 'LA'):
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Gerar thumbnail mantendo proporção
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Salvar em buffer
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            return buffer.getvalue()
    
    async def validate_image_integrity(self, image_data: bytes) -> bool:
        """
        Valida a integridade de uma imagem.
        """
        try:
            format_info = await self._detect_format(image_data, "")
            
            if format_info['format'] == 'SVG':
                return await self._validate_svg_integrity(image_data)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._validate_raster_integrity_sync, image_data
                )
        except Exception:
            return False
    
    async def _validate_svg_integrity(self, svg_data: bytes) -> bool:
        """
        Valida integridade de arquivo SVG.
        """
        try:
            ET.fromstring(svg_data.decode('utf-8'))
            return True
        except Exception:
            return False
    
    def _validate_raster_integrity_sync(self, image_data: bytes) -> bool:
        """
        Validação síncrona de integridade para formatos raster.
        """
        try:
            with Image.open(io.BytesIO(image_data)) as image:
                image.verify()
                return True
        except Exception:
            return False
    
    async def get_image_dimensions(self, image_data: bytes) -> Tuple[int, int]:
        """
        Obtém as dimensões de uma imagem.
        """
        try:
            format_info = await self._detect_format(image_data, "")
            
            if format_info['format'] == 'SVG':
                return await self._get_svg_dimensions(image_data)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._get_raster_dimensions_sync, image_data
                )
        except Exception as e:
            raise ValueError(f"Erro ao obter dimensões da imagem: {str(e)}")
    
    async def _get_svg_dimensions(self, svg_data: bytes) -> Tuple[int, int]:
        """
        Obtém dimensões de arquivo SVG.
        """
        try:
            svg_text = svg_data.decode('utf-8')
            root = ET.fromstring(svg_text)
            
            width = self._extract_numeric_value(root.get('width', ''))
            height = self._extract_numeric_value(root.get('height', ''))
            
            if width and height:
                return (int(width), int(height))
            
            # Tentar viewBox se dimensões não estão disponíveis
            viewbox = root.get('viewBox', '')
            if viewbox:
                try:
                    vb_parts = viewbox.split()
                    if len(vb_parts) >= 4:
                        return (int(float(vb_parts[2])), int(float(vb_parts[3])))
                except (ValueError, IndexError):
                    pass
            
            # Valores padrão se não conseguir determinar
            return (100, 100)
            
        except Exception as e:
            raise ValueError(f"Erro ao obter dimensões SVG: {str(e)}")
    
    def _get_raster_dimensions_sync(self, image_data: bytes) -> Tuple[int, int]:
        """
        Obtenção síncrona de dimensões para formatos raster.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            return image.size
    
    async def extract_exif_data(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extrai dados EXIF de uma imagem.
        """
        try:
            format_info = await self._detect_format(image_data, "")
            
            if format_info['format'] == 'SVG':
                return {}  # SVG não possui dados EXIF
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._extract_exif_data_sync, image_data
                )
        except Exception as e:
            raise ValueError(f"Erro ao extrair dados EXIF: {str(e)}")
    
    def _extract_exif_data_sync(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extração síncrona de dados EXIF.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            return self._extract_exif_sync(image)