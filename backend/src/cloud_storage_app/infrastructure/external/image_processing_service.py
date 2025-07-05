"""
Implementação concreta do serviço de processamento de imagens.
"""
import asyncio
from typing import Dict, Any, Tuple, Set, Optional
from datetime import datetime
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPS
import io
import os
import mimetypes
import xml.etree.ElementTree as ET
import re

from ...domain.services.image_processing_interface import ImageProcessingService


class PillowImageProcessingService(ImageProcessingService):
    """
    Implementação do serviço de processamento de imagens usando Pillow (PIL).
    Suporta: JPEG, PNG, GIF, SVG, WebP, BMP, TIFF com extensibilidade para novos formatos.
    """
    
    def __init__(self):
        # Formatos de imagem suportados organizados por tipo (CORRIGIDO: usar minúsculas)
        self._supported_formats = {
            # Formatos raster (bitmap)
            'raster': {'jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp', 'tiff'},
            # Formatos vetoriais
            'vector': {'svg'},
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
            'bmp': 'image/bmp',
            'tiff': 'image/tiff',
            'svg': 'image/svg+xml'
        }
        
        # Configurações específicas por formato (CORRIGIDO: usar minúsculas)
        self._format_config = {
            'jpeg': {'quality_range': (1, 100), 'supports_transparency': False},
            'png': {'compression_range': (0, 9), 'supports_transparency': True},
            'gif': {'supports_animation': True, 'supports_transparency': True},
            'webp': {'quality_range': (1, 100), 'supports_transparency': True, 'supports_animation': True},
            'bmp': {'supports_transparency': False},
            'tiff': {'supports_transparency': True},
            'svg': {'is_vector': True, 'supports_transparency': True}
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
        """
        if format_type not in self._supported_formats:
            self._supported_formats[format_type] = set()
        
        # CORRIGIDO: usar minúsculas
        self._supported_formats[format_type].add(format_name.lower())
        
        if mime_type:
            self._mime_types[format_name.lower()] = mime_type
        
        if config:
            self._format_config[format_name.lower()] = config
    
    def is_format_supported(self, format_name: str) -> bool:
        """Verifica se um formato é suportado."""
        return format_name.lower() in self.supported_formats
    
    def is_vector_format(self, format_name: str) -> bool:
        """Verifica se um formato é vetorial."""
        return format_name.lower() in self._supported_formats['vector']
    
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
                'format': 'svg',  # CORRIGIDO: usar minúsculas
                'is_vector': True,
                'mime_type': 'image/svg+xml'
            }
        
        # Para formatos raster, usar PIL
        try:
            with Image.open(io.BytesIO(image_data)) as image:
                format_name = image.format.lower() if image.format else 'unknown'  # CORRIGIDO
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
                    'format': ext,  # CORRIGIDO: já em minúsculas
                    'is_vector': ext in self._supported_formats['vector'],
                    'mime_type': self._mime_types[ext]
                }
            raise ValueError(f"Formato de imagem não suportado: {filename}")
    
    def _is_svg_data(self, data: bytes) -> bool:
        """
        Verifica se os dados representam um arquivo SVG.
        """
        try:
            text = data.decode('utf-8', errors='ignore')
            return '<svg' in text.lower() or ('<?xml' in text.lower() and '<svg' in text.lower())
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
                'width': int(numeric_width) if numeric_width else None,
                'height': int(numeric_height) if numeric_height else None,
                'color_depth': None,
                'dpi': None,
                'has_transparency': True,
                'compression': None,
                'camera_make': None,
                'camera_model': None,
                'taken_at': None,
                'gps_latitude': None,
                'gps_longitude': None,
                
                # Metadados gerais
                'format': 'svg',  # CORRIGIDO: usar minúsculas
                'mime_type': 'image/svg+xml',
                'file_size': len(image_data),
                'is_vector': True,
                'is_animated': bool(list(root.iter('{http://www.w3.org/2000/svg}animate')) or 
                                  list(root.iter('{http://www.w3.org/2000/svg}animateTransform'))),
                
                # Informações específicas do SVG
                'svg_info': {
                    'namespace': root.tag if '}' in root.tag else None,
                    'elements_count': len(list(root.iter())),
                    'has_text': bool(list(root.iter('{http://www.w3.org/2000/svg}text'))),
                    'has_images': bool(list(root.iter('{http://www.w3.org/2000/svg}image'))),
                    'viewbox': viewbox,
                    'width_original': width,
                    'height_original': height
                }
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
            width, height = image.size
            mode = image.mode
            format_name = image.format.lower() if image.format else 'unknown'  # CORRIGIDO
            
            color_depth = self._calculate_color_depth(mode)
            
            dpi = image.info.get('dpi', (72, 72))
            dpi_value = dpi[0] if isinstance(dpi, tuple) else dpi
            
            exif_data = self._extract_exif_sync(image)
            
            is_animated = getattr(image, 'is_animated', False)
            
            camera_make = exif_data.get('Make')
            camera_model = exif_data.get('Model')
            taken_at = self._extract_datetime_from_exif(exif_data)
            gps_lat, gps_lon = self._extract_gps_from_exif(exif_data)
            
            compression = self._determine_compression(image, format_name)
            
            metadata = {
                'width': width,
                'height': height,
                'color_depth': color_depth,
                'dpi': dpi_value,
                'has_transparency': self._has_transparency(image),
                'compression': compression,
                'camera_make': camera_make,
                'camera_model': camera_model,
                'taken_at': taken_at,
                'gps_latitude': gps_lat,
                'gps_longitude': gps_lon,
                
                # Metadados gerais
                'format': format_name,
                'mime_type': format_info['mime_type'],
                'file_size': len(image_data),
                'is_vector': False,
                'is_animated': is_animated,
                'color_mode': mode,
                
                # Dados EXIF completos
                'exif_data': exif_data,
                
                # Informações específicas do formato
                'format_info': self._get_format_specific_info(format_name, image)
            }
            
            return metadata
    
    def _extract_datetime_from_exif(self, exif_data: Dict[str, Any]) -> Optional[str]:
        """
        Extrai data/hora da foto dos dados EXIF.
        """
        # Campos EXIF que podem conter data/hora
        datetime_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
        
        for field in datetime_fields:
            if field in exif_data:
                try:
                    # Converter para formato ISO se necessário
                    datetime_str = str(exif_data[field])
                    # EXIF usa formato "YYYY:MM:DD HH:MM:SS"
                    if ':' in datetime_str and len(datetime_str) >= 19:
                        # Converter para ISO format
                        iso_str = datetime_str.replace(':', '-', 2)
                        return iso_str
                    return datetime_str
                except:
                    continue
        
        return None
    
    def _extract_gps_from_exif(self, exif_data: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
        """
        Extrai coordenadas GPS dos dados EXIF.
        """
        try:
            # Verificar se há dados GPS
            if 'GPS' in exif_data or 'GPSInfo' in exif_data:
                gps_info = exif_data.get('GPS') or exif_data.get('GPSInfo')
                
                if gps_info:
                    lat = self._convert_gps_coordinate(gps_info.get('GPSLatitude'), 
                                                     gps_info.get('GPSLatitudeRef'))
                    lon = self._convert_gps_coordinate(gps_info.get('GPSLongitude'), 
                                                     gps_info.get('GPSLongitudeRef'))
                    
                    return lat, lon
        except:
            pass
        
        return None, None
    
    def _convert_gps_coordinate(self, coordinate, ref) -> Optional[float]:
        """
        Converte coordenada GPS do formato EXIF para decimal.
        """
        if not coordinate or not ref:
            return None
        
        try:
            # Coordinate é uma tupla de frações (degrees, minutes, seconds)
            if isinstance(coordinate, (list, tuple)) and len(coordinate) >= 3:
                degrees = float(coordinate[0])
                minutes = float(coordinate[1])
                seconds = float(coordinate[2])
                
                decimal = degrees + minutes/60 + seconds/3600
                
                # Aplicar referência (N/S para latitude, E/W para longitude)
                if ref in ['S', 'W']:
                    decimal = -decimal
                
                return decimal
        except:
            pass
        
        return None
    
    def _determine_compression(self, image: Image.Image, format_name: str) -> Optional[str]:
        """
        Determina o tipo de compressão da imagem.
        """
        if format_name == 'jpeg':  # CORRIGIDO: usar minúsculas
            return 'JPEG'
        elif format_name == 'png':
            return image.info.get('compression', 'PNG')
        elif format_name == 'gif':
            return 'LZW'
        elif format_name == 'webp':
            return 'WebP'
        elif format_name == 'tiff':
            return image.info.get('compression', 'TIFF')
        
        return None
    
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
            
            for key, value in config.items():
                if key.startswith('supports_'):
                    info[key] = value
        
        if hasattr(image, 'info'):
            if format_name == 'png':
                info['compression'] = image.info.get('compression', 'unknown')
            elif format_name == 'jpeg':
                info['quality'] = image.info.get('quality', 'unknown')
            elif format_name in ('gif', 'webp'):
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
                        # Manter tuplas para coordenadas GPS
                        if tag in ['GPSLatitude', 'GPSLongitude']:
                            value = value
                        else:
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
            
            if format_info['format'] == 'svg':
                return await self._generate_svg_thumbnail_placeholder(image_data, size)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._generate_raster_thumbnail_sync, image_data, size
                )
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail: {str(e)}")
    
    async def _generate_svg_thumbnail_placeholder(self, svg_data: bytes, size: Tuple[int, int]) -> bytes:
        """
        Gera placeholder para thumbnail SVG.
        """
        placeholder_image = Image.new('RGB', size, (240, 240, 240))
        buffer = io.BytesIO()
        placeholder_image.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_raster_thumbnail_sync(self, image_data: bytes, size: Tuple[int, int]) -> bytes:
        """
        Geração síncrona de thumbnail para formatos raster.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            # Converter para RGB se necessário
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
            
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
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