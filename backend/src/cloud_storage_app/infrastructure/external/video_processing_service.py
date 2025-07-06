"""
Implementação do serviço de processamento de vídeos.
Extrai metadados, gera thumbnails e processa diferentes versões/qualidades.
"""
import asyncio
import subprocess
import tempfile
import os
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
from pathlib import Path

from ...domain.services.video_processing_interface import VideoProcessingService
from ...domain.entities.video_file import VideoFile
from ...domain.value_objects import VideoVersion, FilePath
from ..external.thumbnail_generator_service import (
    PillowThumbnailGeneratorService, 
    ThumbnailQuality
)


class FFmpegVideoProcessingService(VideoProcessingService):
    """
    Implementação do serviço de processamento de vídeos usando FFmpeg.
    Processa metadados, gera thumbnails e cria versões em diferentes qualidades.
    """
    
    def __init__(self, thumbnail_service: Optional[PillowThumbnailGeneratorService] = None):
        """
        Inicializa o serviço de processamento de vídeos.
        
        Args:
            thumbnail_service: Serviço de geração de thumbnails (opcional)
        """
        self.thumbnail_service = thumbnail_service or PillowThumbnailGeneratorService()
        
        # Formatos suportados conforme especificação
        self.supported_formats = ['mp4', 'avi', 'mov', 'webm']
        
        # Configurações de qualidade para processamento
        self.quality_profiles = {
            '2160p': {
                'resolution': '3840x2160',
                'bitrate': '8000k',
                'audio_bitrate': '192k',
                'preset': 'medium',
                'crf': '23'
            },
            '1080p': {
                'resolution': '1920x1080',
                'bitrate': '4000k',
                'audio_bitrate': '128k',
                'preset': 'medium',
                'crf': '23'
            },
            '720p': {
                'resolution': '1280x720',
                'bitrate': '2000k',
                'audio_bitrate': '128k',
                'preset': 'medium',
                'crf': '23'
            },
            '480p': {
                'resolution': '854x480',
                'bitrate': '1000k',
                'audio_bitrate': '96k',
                'preset': 'medium',
                'crf': '23'
            },
            '360p': {
                'resolution': '640x360',
                'bitrate': '500k',
                'audio_bitrate': '64k',
                'preset': 'medium',
                'crf': '23'
            }
        }
    
    async def is_ffmpeg_available(self) -> bool:
        """
        Verifica se o FFmpeg está disponível no sistema.
        """
        try:
            result = await asyncio.create_subprocess_exec(
                'ffmpeg', '-version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    async def is_format_supported(self, format_name: str) -> bool:
        """
        Verifica se um formato de vídeo é suportado.
        """
        return format_name.lower() in self.supported_formats
    
    async def extract_video_metadata(self, video_data: bytes) -> Dict[str, Any]:
        """
        Extrai metadados detalhados de um arquivo de vídeo.
        
        Args:
            video_data: Dados binários do vídeo
            
        Returns:
            Dict com metadados do vídeo
        """
        if not await self.is_ffmpeg_available():
            raise RuntimeError("FFmpeg não está disponível no sistema")
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.tmp', delete=False) as temp_file:
            temp_file.write(video_data)
            temp_path = temp_file.name
        
        try:
            # Extrair metadados usando ffprobe
            metadata = await self._extract_metadata_with_ffprobe(temp_path)
            
            # Processar e estruturar os metadados
            return await self._process_video_metadata(metadata, len(video_data))
            
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def _extract_metadata_with_ffprobe(self, video_path: str) -> Dict[str, Any]:
        """
        Extrai metadados usando ffprobe.
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise ValueError(f"FFprobe falhou: {stderr.decode()}")
        
        return json.loads(stdout.decode())
    
    async def _process_video_metadata(self, ffprobe_data: Dict[str, Any], file_size: int) -> Dict[str, Any]:
        """
        Processa dados do ffprobe e retorna metadados estruturados.
        """
        format_info = ffprobe_data.get('format', {})
        streams = ffprobe_data.get('streams', [])
        
        # Encontrar stream de vídeo
        video_stream = None
        audio_stream = None
        
        for stream in streams:
            if stream.get('codec_type') == 'video':
                video_stream = stream
            elif stream.get('codec_type') == 'audio':
                audio_stream = stream
        
        if not video_stream:
            raise ValueError("Nenhum stream de vídeo encontrado")
        
        # Extrair informações básicas
        duration = float(format_info.get('duration', 0))
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        
        # Calcular frame rate
        frame_rate = self._calculate_frame_rate(video_stream)
        
        # Extrair codecs
        video_codec = video_stream.get('codec_name', 'unknown')
        audio_codec = audio_stream.get('codec_name', 'unknown') if audio_stream else None
        
        # Calcular bitrate
        bitrate = int(format_info.get('bit_rate', 0))
        
        # Determinar se tem áudio
        has_audio = audio_stream is not None
        
        # Verificar se tem legendas
        has_subtitles = any(
            stream.get('codec_type') == 'subtitle' 
            for stream in streams
        )
        
        # Extrair informações adicionais
        created_with = format_info.get('tags', {}).get('encoder', None)
        
        return {
            'duration_seconds': int(duration),
            'width': width,
            'height': height,
            'frame_rate': frame_rate,
            'bitrate': bitrate,
            'video_codec': video_codec,
            'audio_codec': audio_codec,
            'has_audio': has_audio,
            'has_subtitles': has_subtitles,
            'created_with': created_with,
            'file_size': file_size,
            'format': format_info.get('format_name', 'unknown'),
            'streams_count': len(streams),
            'video_stream_info': {
                'profile': video_stream.get('profile'),
                'level': video_stream.get('level'),
                'pix_fmt': video_stream.get('pix_fmt'),
                'color_space': video_stream.get('color_space'),
                'color_range': video_stream.get('color_range')
            },
            'audio_stream_info': {
                'sample_rate': audio_stream.get('sample_rate') if audio_stream else None,
                'channels': audio_stream.get('channels') if audio_stream else None,
                'channel_layout': audio_stream.get('channel_layout') if audio_stream else None
            } if audio_stream else None
        }
    
    def _calculate_frame_rate(self, video_stream: Dict[str, Any]) -> Optional[float]:
        """
        Calcula o frame rate do vídeo.
        """
        # Tentar diferentes campos para frame rate
        fps_fields = ['r_frame_rate', 'avg_frame_rate', 'time_base']
        
        for field in fps_fields:
            if field in video_stream:
                fps_str = video_stream[field]
                if fps_str and '/' in fps_str:
                    try:
                        num, den = fps_str.split('/')
                        fps = float(num) / float(den)
                        if fps > 0:
                            return round(fps, 2)
                    except (ValueError, ZeroDivisionError):
                        continue
        
        return None
    
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
        return await self.thumbnail_service.generate_video_thumbnail(
            video_data=video_data,
            timestamp=timestamp,
            size=size,
            quality=quality
        )
    
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
        thumbnails = []
        
        for timestamp in timestamps:
            try:
                thumbnail = await self.generate_thumbnail(
                    video_data=video_data,
                    timestamp=timestamp,
                    size=size,
                    quality=quality
                )
                thumbnails.append(thumbnail)
            except Exception as e:
                # Em caso de erro, adicionar placeholder
                placeholder = await self.thumbnail_service._generate_video_placeholder(
                    size=size,
                    quality=quality,
                    error_msg=f"Erro no timestamp {timestamp}s"
                )
                thumbnails.append(placeholder)
        
        return thumbnails
    
    async def get_video_info(self, video_data: bytes) -> Dict[str, Any]:
        """
        Retorna informações básicas sobre o vídeo.
        """
        try:
            metadata = await self.extract_video_metadata(video_data)
            
            return {
                'is_valid': True,
                'duration_seconds': metadata.get('duration_seconds', 0),
                'duration_formatted': self._format_duration(metadata.get('duration_seconds', 0)),
                'resolution': f"{metadata.get('width', 0)}x{metadata.get('height', 0)}",
                'quality_level': self._get_quality_level(metadata.get('height', 0)),
                'file_size': metadata.get('file_size', 0),
                'has_audio': metadata.get('has_audio', False),
                'has_subtitles': metadata.get('has_subtitles', False),
                'codec': metadata.get('video_codec', 'unknown'),
                'frame_rate': metadata.get('frame_rate'),
                'bitrate': metadata.get('bitrate', 0)
            }
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'file_size': len(video_data)
            }
    
    def _format_duration(self, seconds: int) -> str:
        """
        Formata duração em segundos para formato HH:MM:SS.
        """
        if seconds <= 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _get_quality_level(self, height: int) -> str:
        """
        Determina o nível de qualidade baseado na altura.
        """
        if height >= 2160:
            return "4K/UHD"
        elif height >= 1440:
            return "2K/QHD"
        elif height >= 1080:
            return "Full HD"
        elif height >= 720:
            return "HD"
        elif height >= 480:
            return "SD"
        else:
            return "Baixa qualidade"
    
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
            Dict com as versões processadas
        """
        if not await self.is_ffmpeg_available():
            raise RuntimeError("FFmpeg não está disponível para processamento")
        
        versions = {}
        original_height = original_metadata.get('height', 0)
        
        # Criar versão original
        original_resolution = f"{original_metadata.get('width', 0)}x{original_metadata.get('height', 0)}"
        original_quality = self._height_to_quality(original_height)
        
        versions['original'] = VideoVersion(
            resolution=original_quality,
            file_path=FilePath(f"{output_dir}/original.mp4"),
            is_original=True,
            processing_status="completed"
        )
        
        # Filtrar qualidades que não são maiores que o original
        valid_qualities = []
        for quality in target_qualities:
            quality_height = self._get_quality_height(quality)
            if quality_height <= original_height:
                valid_qualities.append(quality)
        
        # Processar cada qualidade
        for quality in valid_qualities:
            try:
                version = await self._process_single_quality(
                    video_data=video_data,
                    quality=quality,
                    output_dir=output_dir
                )
                versions[quality] = version
            except Exception as e:
                # Criar versão com status de erro
                versions[quality] = VideoVersion(
                    resolution=quality,
                    file_path=FilePath(f"{output_dir}/{quality}_failed.mp4"),
                    is_original=False,
                    processing_status="failed"
                )
        
        return versions
    
    async def _process_single_quality(
        self,
        video_data: bytes,
        quality: str,
        output_dir: str
    ) -> VideoVersion:
        """
        Processa uma única versão de qualidade.
        """
        if quality not in self.quality_profiles:
            raise ValueError(f"Qualidade {quality} não suportada")
        
        profile = self.quality_profiles[quality]
        
        # Criar arquivo temporário de entrada
        with tempfile.NamedTemporaryFile(suffix='.tmp', delete=False) as input_file:
            input_file.write(video_data)
            input_path = input_file.name
        
        # Definir caminho de saída
        output_filename = f"{quality}_processed.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Criar versão inicial com status "processing"
        version = VideoVersion(
            resolution=quality,
            file_path=FilePath(output_path),
            is_original=False,
            processing_status="processing"
        )
        
        try:
            # Comando FFmpeg para transcodificação
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', f"scale={profile['resolution']}:force_original_aspect_ratio=decrease",
                '-c:v', 'libx264',
                '-preset', profile['preset'],
                '-crf', profile['crf'],
                '-b:v', profile['bitrate'],
                '-c:a', 'aac',
                '-b:a', profile['audio_bitrate'],
                '-movflags', '+faststart',
                '-y',  # Sobrescrever arquivo existente
                output_path
            ]
            
            # Executar FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise ValueError(f"FFmpeg falhou: {stderr.decode()}")
            
            # Criar versão com status de sucesso
            return VideoVersion(
                resolution=quality,
                file_path=FilePath(output_path),
                is_original=False,
                processing_status="completed"
            )
            
        except Exception as e:
            # Retornar versão com status de erro
            return VideoVersion(
                resolution=quality,
                file_path=FilePath(output_path),
                is_original=False,
                processing_status="failed"
            )
            
        finally:
            # Limpar arquivo temporário de entrada
            try:
                os.unlink(input_path)
            except:
                pass
    
    def _get_quality_height(self, quality: str) -> int:
        """
        Retorna a altura em pixels para uma qualidade específica.
        """
        height_map = {
            '2160p': 2160,
            '4K': 2160,
            '1440p': 1440,
            '2K': 1440,
            '1080p': 1080,
            '720p': 720,
            '480p': 480,
            '360p': 360
        }
        return height_map.get(quality, 0)
    
    def _height_to_quality(self, height: int) -> str:
        """
        Converte altura em pixels para string de qualidade.
        """
        if height >= 2160:
            return "2160p"
        elif height >= 1440:
            return "1440p"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
        elif height >= 360:
            return "360p"
        else:
            return f"{height}p"
    
    async def create_video_versions_async(
        self,
        video_data: bytes,
        original_metadata: Dict[str, Any],
        target_qualities: List[str],
        output_dir: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, VideoVersion]:
        """
        Cria versões de vídeo de forma assíncrona com callback de progresso.
        """
        versions = {}
        total_qualities = len(target_qualities)
        
        # Criar versão original
        original_height = original_metadata.get('height', 0)
        original_quality = self._height_to_quality(original_height)
        
        versions['original'] = VideoVersion(
            resolution=original_quality,
            file_path=FilePath(f"{output_dir}/original.mp4"),
            is_original=True,
            processing_status="completed"
        )
        
        # Processar cada qualidade
        for i, quality in enumerate(target_qualities):
            quality_height = self._get_quality_height(quality)
            
            # Pular se a qualidade for maior que o original
            if quality_height > original_height:
                continue
            
            # Callback de progresso
            if progress_callback:
                progress_callback(quality, i + 1, total_qualities, "processing")
            
            try:
                # Criar versão inicial
                version = VideoVersion(
                    resolution=quality,
                    file_path=FilePath(f"{output_dir}/{quality}_processing.mp4"),
                    is_original=False,
                    processing_status="processing"
                )
                versions[quality] = version
                
                # Processar versão
                processed_version = await self._process_single_quality(
                    video_data=video_data,
                    quality=quality,
                    output_dir=output_dir
                )
                versions[quality] = processed_version
                
                # Callback de sucesso
                if progress_callback:
                    progress_callback(quality, i + 1, total_qualities, "completed")
                
            except Exception as e:
                # Criar versão com erro
                versions[quality] = VideoVersion(
                    resolution=quality,
                    file_path=FilePath(f"{output_dir}/{quality}_failed.mp4"),
                    is_original=False,
                    processing_status="failed"
                )
                
                # Callback de erro
                if progress_callback:
                    progress_callback(quality, i + 1, total_qualities, "failed")
        
        return versions
    
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
        if not await self.is_ffmpeg_available():
            raise RuntimeError("FFmpeg não está disponível")
        
        # Criar arquivo temporário de entrada
        with tempfile.NamedTemporaryFile(suffix='.tmp', delete=False) as input_file:
            input_file.write(video_data)
            input_path = input_file.name
        
        # Criar arquivo temporário de saída
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Comando FFmpeg para criar preview
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ss', str(start_time),
                '-t', str(duration_seconds),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '28',
                '-c:a', 'aac',
                '-b:a', '96k',
                '-movflags', '+faststart',
                '-y',
                output_path
            ]
            
            # Executar FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise ValueError(f"FFmpeg falhou: {stderr.decode()}")
            
            # Ler arquivo de saída
            with open(output_path, 'rb') as f:
                preview_data = f.read()
            
            return preview_data
            
        finally:
            # Limpar arquivos temporários
            try:
                os.unlink(input_path)
                os.unlink(output_path)
            except:
                pass
    
    async def get_supported_formats(self) -> List[str]:
        """
        Retorna lista de formatos suportados.
        """
        return self.supported_formats.copy()
    
    async def validate_video_file(self, video_data: bytes) -> Dict[str, Any]:
        """
        Valida se o arquivo é um vídeo válido.
        
        Returns:
            Dict com informações de validação
        """
        try:
            metadata = await self.extract_video_metadata(video_data)
            
            # Verificar se tem pelo menos um stream de vídeo
            duration = metadata.get('duration_seconds', 0)
            width = metadata.get('width', 0)
            height = metadata.get('height', 0)
            
            is_valid = (
                duration > 0 and
                width > 0 and
                height > 0
            )
            
            warnings = []
            
            # Verificar avisos
            if not metadata.get('has_audio'):
                warnings.append("Vídeo não possui áudio")
            
            if duration > 3600:  # Mais de 1 hora
                warnings.append("Vídeo muito longo (>1 hora)")
            
            if metadata.get('file_size', 0) > 500 * 1024 * 1024:  # Mais de 500MB
                warnings.append("Arquivo muito grande (>500MB)")
            
            return {
                'is_valid': is_valid,
                'metadata': metadata,
                'warnings': warnings,
                'file_size': metadata.get('file_size', 0)
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'file_size': len(video_data)
            }