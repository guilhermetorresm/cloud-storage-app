"""
Interface abstrata para o serviço de processamento de vídeos.
Define os contratos para extração de metadados, geração de thumbnails e processamento de qualidade.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union
from ..value_objects import VideoVersion
from .thumbnail_generator_interface import ThumbnailQuality


class VideoProcessingService(ABC):
    """
    Interface abstrata para serviços de processamento de vídeos.
    
    Define os métodos necessários para:
    - Extrair metadados de vídeos
    - Gerar thumbnails
    - Processar diferentes qualidades
    - Validar arquivos de vídeo
    """
    
    @abstractmethod
    async def is_ffmpeg_available(self) -> bool:
        """
        Verifica se o FFmpeg está disponível no sistema.
        
        Returns:
            bool: True se FFmpeg estiver disponível
        """
        pass
    
    @abstractmethod
    async def is_format_supported(self, format_name: str) -> bool:
        """
        Verifica se um formato de vídeo é suportado.
        
        Args:
            format_name: Nome do formato (ex: 'mp4', 'avi')
            
        Returns:
            bool: True se o formato for suportado
        """
        pass
    
    @abstractmethod
    async def extract_video_metadata(self, video_data: bytes) -> Dict[str, Any]:
        """
        Extrai metadados detalhados de um arquivo de vídeo.
        
        Args:
            video_data: Dados binários do vídeo
            
        Returns:
            Dict com metadados incluindo:
            - duration_seconds: Duração em segundos
            - width: Largura em pixels
            - height: Altura em pixels
            - frame_rate: Taxa de quadros
            - bitrate: Taxa de bits
            - video_codec: Codec de vídeo
            - audio_codec: Codec de áudio
            - has_audio: Se possui áudio
            - has_subtitles: Se possui legendas
            - created_with: Software usado para criar
            - file_size: Tamanho do arquivo
        """
        pass
    
    @abstractmethod
    async def generate_thumbnail(
        self, 
        video_data: bytes, 
        timestamp: float = 0.0,
        size: Tuple[int, int] = (200, 150),
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> bytes:
        """
        Gera thumbnail de um vídeo.
        
        Args:
            video_data: Dados binários do vídeo
            timestamp: Timestamp do frame (padrão: 0.0 para primeiro frame)
            size: Tamanho da thumbnail (largura, altura)
            quality: Qualidade da thumbnail
            
        Returns:
            bytes: Dados da thumbnail em formato JPEG
        """
        pass
    
    @abstractmethod
    async def generate_multiple_thumbnails(
        self,
        video_data: bytes,
        timestamps: List[float],
        size: Tuple[int, int] = (200, 150),
        quality: ThumbnailQuality = ThumbnailQuality.MEDIUM
    ) -> List[bytes]:
        """
        Gera múltiplas thumbnails de um vídeo em diferentes timestamps.
        
        Args:
            video_data: Dados binários do vídeo
            timestamps: Lista de timestamps para extrair frames
            size: Tamanho das thumbnails
            quality: Qualidade das thumbnails
            
        Returns:
            List[bytes]: Lista com dados das thumbnails
        """
        pass
    
    @abstractmethod
    async def get_video_info(self, video_data: bytes) -> Dict[str, Any]:
        """
        Retorna informações básicas sobre o vídeo.
        
        Args:
            video_data: Dados binários do vídeo
            
        Returns:
            Dict com informações básicas:
            - is_valid: Se o vídeo é válido
            - duration_seconds: Duração
            - duration_formatted: Duração formatada
            - resolution: Resolução formatada
            - quality_level: Nível de qualidade
            - file_size: Tamanho do arquivo
            - has_audio: Se possui áudio
            - codec: Codec principal
        """
        pass
    
    @abstractmethod
    async def process_video_quality_versions(
        self,
        video_data: bytes,
        original_metadata: Dict[str, Any],
        target_qualities: List[str],
        output_dir: str
    ) -> Dict[str, VideoVersion]:
        """
        Processa o vídeo em diferentes qualidades.
        
        Args:
            video_data: Dados binários do vídeo original
            original_metadata: Metadados do vídeo original
            target_qualities: Lista de qualidades desejadas (ex: ['1080p', '720p', '480p'])
            output_dir: Diretório para salvar as versões processadas
            
        Returns:
            Dict com as versões processadas por qualidade
        """
        pass
    
    @abstractmethod
    async def create_video_preview(
        self,
        video_data: bytes,
        duration_seconds: int = 30,
        start_time: float = 0.0
    ) -> bytes:
        """
        Cria um preview/trailer do vídeo com duração específica.
        
        Args:
            video_data: Dados binários do vídeo
            duration_seconds: Duração do preview em segundos
            start_time: Tempo de início do preview
            
        Returns:
            bytes: Dados do preview em formato MP4
        """
        pass
    
    @abstractmethod
    async def get_supported_formats(self) -> List[str]:
        """
        Retorna lista de formatos suportados.
        
        Returns:
            List[str]: Lista de formatos suportados
        """
        pass
    
    @abstractmethod
    async def validate_video_file(self, video_data: bytes) -> Dict[str, Any]:
        """
        Valida se o arquivo é um vídeo válido.
        
        Args:
            video_data: Dados binários do vídeo
            
        Returns:
            Dict com informações de validação:
            - is_valid: Se o arquivo é válido
            - metadata: Metadados extraídos
            - warnings: Lista de avisos
            - errors: Lista de erros (se houver)
        """
        pass