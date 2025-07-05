"""
Implementação concreta do serviço unificado de geração de miniaturas.
"""
import asyncio
from typing import Tuple, Optional
from PIL import Image, ImageOps
import io

from ...domain.services.thumbnail_generator_interface import (
    ThumbnailGeneratorService,
    ThumbnailFormat,
    ThumbnailQuality
)


class PillowThumbnailGeneratorService(ThumbnailGeneratorService):
    """
    Implementação do serviço unificado de geração de miniaturas usando Pillow.
    
    Por enquanto implementa apenas geração de thumbnails para imagens.
    A implementação para vídeos será adicionada futuramente.
    """
    
    def __init__(self):
        # Formatos de imagem suportados
        self.supported_image_formats = [
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'
        ]
        
        # Formatos de vídeo suportados (para implementação futura)
        self.supported_video_formats = [
            'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'
        ]
    
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
            return await asyncio.get_event_loop().run_in_executor(
                None, self._generate_image_thumbnail_sync, image_data, size, format, quality
            )
        except Exception as e:
            raise ValueError(f"Erro ao gerar thumbnail de imagem: {str(e)}")
    
    def _generate_image_thumbnail_sync(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        format: ThumbnailFormat,
        quality: ThumbnailQuality
    ) -> bytes:
        """
        Geração síncrona de thumbnail de imagem.
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
        """
        if format == ThumbnailFormat.JPEG:
            # JPEG não suporta transparência, converter para RGB com fundo branco
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
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
        
        elif format == ThumbnailFormat.PNG:
            # PNG suporta transparência
            if image.mode == 'P':
                return image.convert('RGBA')
            elif image.mode not in ('RGB', 'RGBA'):
                return image.convert('RGBA')
            return image
        
        elif format == ThumbnailFormat.WEBP:
            # WebP suporta transparência
            if image.mode == 'P':
                return image.convert('RGBA')
            elif image.mode not in ('RGB', 'RGBA'):
                return image.convert('RGBA')
            return image
        
        return image
    
    def _get_save_kwargs(self, format: ThumbnailFormat, quality: ThumbnailQuality) -> dict:
        """
        Obtém argumentos de salvamento baseados no formato e qualidade.
        """
        base_kwargs = {
            'format': format.value,
            'optimize': True
        }
        
        if format in (ThumbnailFormat.JPEG, ThumbnailFormat.WEBP):
            base_kwargs['quality'] = quality.value
        
        if format == ThumbnailFormat.PNG:
            # PNG não usa quality, mas podemos otimizar
            base_kwargs['compress_level'] = 6
        
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
            return await asyncio.get_event_loop().run_in_executor(
                None, self._resize_image_sync, image_data, size, maintain_aspect_ratio, format
            )
        except Exception as e:
            raise ValueError(f"Erro ao redimensionar imagem: {str(e)}")
    
    def _resize_image_sync(
        self, 
        image_data: bytes, 
        size: Tuple[int, int],
        maintain_aspect_ratio: bool,
        format: Optional[ThumbnailFormat]
    ) -> bytes:
        """
        Redimensionamento síncrono de imagem.
        """
        with Image.open(io.BytesIO(image_data)) as image:
            original_format = image.format
            
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
                if original_format in ['JPEG', 'PNG', 'WEBP']:
                    output_format = ThumbnailFormat(original_format)
                else:
                    output_format = ThumbnailFormat.JPEG
                
                image = self._prepare_image_for_format(image, output_format)
                save_kwargs = self._get_save_kwargs(output_format, ThumbnailQuality.HIGH)
            
            # Salvar resultado
            buffer = io.BytesIO()
            image.save(buffer, **save_kwargs)
            buffer.seek(0)
            
            return buffer.getvalue()
    
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