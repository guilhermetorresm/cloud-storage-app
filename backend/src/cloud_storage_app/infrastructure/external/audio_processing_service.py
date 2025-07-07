"""
Implementação concreta do serviço de processamento de áudio.
"""
import asyncio
import io
import mimetypes
import os
from typing import Dict, Any, Optional, Set, Tuple
from datetime import datetime
import struct
import json

try:
    import mutagen
    from mutagen.id3 import ID3
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    from mutagen.wave import WAVE
    from mutagen._util import MutagenError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

from ...domain.services.audio_processing_interface import AudioProcessingService


class MutagenAudioProcessingService(AudioProcessingService):
    """
    Implementação do serviço de processamento de áudio usando Mutagen.
    Suporta: MP3, WAV, OGG, FLAC com extensibilidade para novos formatos.
    """
    
    def __init__(self):
        """
        Inicializa o serviço de processamento de áudio.
        """
        if not MUTAGEN_AVAILABLE:
            raise ImportError("Biblioteca mutagen não está disponível. Instale com: pip install mutagen")
        
        # Formatos de áudio suportados
        self._supported_formats = {
            # Formatos com perda (lossy)
            'lossy': {'mp3', 'ogg', 'aac', 'm4a'},
            # Formatos sem perda (lossless)
            'lossless': {'flac', 'wav', 'aiff', 'alac'},
            # Formatos especiais/futuros
            'special': set()
        }
        
        # Mapeamento de extensões para tipos MIME
        self._mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
            'm4a': 'audio/mp4',
            'aiff': 'audio/aiff',
            'alac': 'audio/alac'
        }
        
        # Mapeamento de extensões para classes Mutagen
        self._mutagen_classes = {
            'mp3': MP3,
            'flac': FLAC,
            'ogg': OggVorbis,
            'wav': WAVE
        }
        
        # Configurações específicas por formato
        self._format_config = {
            'mp3': {
                'is_lossy': True,
                'typical_bitrates': [128, 192, 256, 320],
                'supports_id3': True,
                'supports_vbr': True
            },
            'wav': {
                'is_lossy': False,
                'typical_sample_rates': [44100, 48000, 96000, 192000],
                'supports_id3': False,
                'supports_vbr': False
            },
            'flac': {
                'is_lossy': False,
                'compression_levels': range(0, 9),
                'supports_vorbis_comments': True,
                'supports_vbr': False
            },
            'ogg': {
                'is_lossy': True,
                'typical_bitrates': [64, 128, 192, 256, 320],
                'supports_vorbis_comments': True,
                'supports_vbr': True
            }
        }
    
    @property
    def supported_formats(self) -> Set[str]:
        """Retorna todos os formatos suportados."""
        all_formats = set()
        for format_group in self._supported_formats.values():
            all_formats.update(format_group)
        return all_formats
    
    def get_supported_formats(self) -> Set[str]:
        """Retorna os formatos de áudio suportados."""
        return self.supported_formats
    
    def is_format_supported(self, format_name: str) -> bool:
        """Verifica se um formato é suportado."""
        return format_name.lower() in self.supported_formats
    
    def is_lossy_format(self, format_name: str) -> bool:
        """Verifica se um formato usa compressão com perda."""
        return format_name.lower() in self._supported_formats['lossy']
    
    def is_audio_format_valid_for_entity(self, format_name: str) -> bool:
        """
        Verifica se o formato é válido para a entidade AudioFile.
        Todos os formatos suportados são válidos para AudioFile.
        """
        return self.is_format_supported(format_name)
    
    def add_supported_format(self, format_name: str, format_type: str = 'special',
                           mime_type: Optional[str] = None, config: Optional[Dict] = None):
        """
        Adiciona suporte para um novo formato de áudio.
        """
        if format_type not in self._supported_formats:
            self._supported_formats[format_type] = set()
        
        self._supported_formats[format_type].add(format_name.lower())
        
        if mime_type:
            self._mime_types[format_name.lower()] = mime_type
        
        if config:
            self._format_config[format_name.lower()] = config
    
    async def extract_metadata(self, audio_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extrai metadados completos de um arquivo de áudio.
        Retorna APENAS os campos esperados pela entidade AudioFile.
        """
        try:
            # Determinar formato baseado no conteúdo e extensão
            format_info = await self._detect_format(audio_data, filename)
            
            # Verificar se o formato é suportado pela entidade AudioFile
            if not self.is_audio_format_valid_for_entity(format_info['format']):
                raise ValueError(f"Formato {format_info['format']} não é suportado pela entidade AudioFile")
            
            return await asyncio.get_event_loop().run_in_executor(
                None, self._extract_metadata_sync, audio_data, filename, format_info
            )
        except Exception as e:
            raise ValueError(f"Erro ao extrair metadados do áudio: {str(e)}")
    
    async def _detect_format(self, audio_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Detecta o formato do áudio baseado no conteúdo e extensão.
        """
        # Primeiro, tentar detectar pelo cabeçalho do arquivo
        format_from_header = self._detect_format_from_header(audio_data)
        
        # Se detectou pelo cabeçalho, usar essa informação
        if format_from_header:
            format_name = format_from_header
        else:
            # Fallback para extensão do arquivo
            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if ext in self._mime_types:
                format_name = ext
            else:
                raise ValueError(f"Formato de áudio não suportado: {filename}")
        
        return {
            'format': format_name,
            'is_lossy': self.is_lossy_format(format_name),
            'mime_type': self._get_mime_type(format_name, filename)
        }
    
    def _detect_format_from_header(self, audio_data: bytes) -> Optional[str]:
        """
        Detecta o formato do áudio baseado no cabeçalho do arquivo.
        """
        if len(audio_data) < 16:
            return None
        
        # MP3 - verifica magic bytes
        if (audio_data.startswith(b'ID3') or 
            audio_data.startswith(b'\xff\xfb') or 
            audio_data.startswith(b'\xff\xfa')):
            return 'mp3'
        
        # WAV - verifica RIFF header
        if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]:
            return 'wav'
        
        # FLAC - verifica magic bytes
        if audio_data.startswith(b'fLaC'):
            return 'flac'
        
        # OGG - verifica magic bytes
        if audio_data.startswith(b'OggS'):
            return 'ogg'
        
        return None
    
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
        return f"audio/{format_name.lower()}" if format_name else "audio/unknown"
    
    def _extract_metadata_sync(self, audio_data: bytes, filename: str, format_info: Dict) -> Dict[str, Any]:
        """
        Extração síncrona de metadados para formatos de áudio.
        Retorna APENAS os campos esperados pela entidade AudioFile.
        """
        try:
            # Criar um objeto BytesIO para o Mutagen
            audio_file_obj = io.BytesIO(audio_data)
            
            # Tentar carregar o arquivo com Mutagen
            audiofile = mutagen.File(audio_file_obj)
            
            if audiofile is None:
                # Se Mutagen não conseguir carregar, tentar análise manual
                return self._extract_metadata_manual(audio_data, format_info)
            
            # Extrair propriedades básicas
            duration_seconds = getattr(audiofile.info, 'length', None)
            bitrate = getattr(audiofile.info, 'bitrate', None)
            sample_rate = getattr(audiofile.info, 'sample_rate', None)
            channels = getattr(audiofile.info, 'channels', None)
            
            # Extrair gênero das tags
            genre = self._extract_genre_from_tags(audiofile)
            
            # Retornar APENAS os campos esperados pela entidade AudioFile
            return {
                'duration_seconds': int(duration_seconds) if duration_seconds else None,
                'bitrate': int(bitrate) if bitrate else None,
                'sample_rate': int(sample_rate) if sample_rate else None,
                'channels': int(channels) if channels else None,
                'genre': genre
            }
            
        except Exception as e:
            # Em caso de erro, tentar análise manual
            return self._extract_metadata_manual(audio_data, format_info)
    
    def _extract_genre_from_tags(self, audiofile) -> Optional[str]:
        """
        Extrai o gênero das tags do arquivo de áudio.
        """
        if not audiofile.tags:
            return None
        
        # Tentar diferentes campos de gênero
        genre_fields = ['TCON', 'GENRE', 'genre', 'Genre']
        
        for field in genre_fields:
            if field in audiofile.tags:
                genre_value = audiofile.tags[field]
                if isinstance(genre_value, list) and len(genre_value) > 0:
                    return str(genre_value[0])
                elif isinstance(genre_value, str):
                    return genre_value
        
        return None
    
    def _extract_metadata_manual(self, audio_data: bytes, format_info: Dict) -> Dict[str, Any]:
        """
        Extração manual de metadados quando Mutagen falha.
        """
        format_name = format_info['format']
        
        # Tentar análise específica por formato
        if format_name == 'wav':
            return self._extract_wav_metadata_manual(audio_data)
        elif format_name == 'mp3':
            return self._extract_mp3_metadata_manual(audio_data)
        else:
            # Retornar valores padrão
            return {
                'duration_seconds': None,
                'bitrate': None,
                'sample_rate': None,
                'channels': None,
                'genre': None
            }
    
    def _extract_wav_metadata_manual(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extração manual de metadados WAV.
        """
        try:
            if len(audio_data) < 44:
                return self._get_default_metadata()
            
            # Verificar cabeçalho RIFF
            if not audio_data.startswith(b'RIFF'):
                return self._get_default_metadata()
            
            # Extrair informações do cabeçalho WAV
            channels = struct.unpack('<H', audio_data[22:24])[0]
            sample_rate = struct.unpack('<L', audio_data[24:28])[0]
            byte_rate = struct.unpack('<L', audio_data[28:32])[0]
            bits_per_sample = struct.unpack('<H', audio_data[34:36])[0]
            
            # Calcular duração aproximada
            data_size = len(audio_data) - 44  # Tamanho aproximado dos dados
            duration_seconds = data_size / byte_rate if byte_rate > 0 else None
            
            # Calcular bitrate
            bitrate = (byte_rate * 8) // 1000 if byte_rate > 0 else None
            
            return {
                'duration_seconds': int(duration_seconds) if duration_seconds else None,
                'bitrate': int(bitrate) if bitrate else None,
                'sample_rate': int(sample_rate) if sample_rate else None,
                'channels': int(channels) if channels else None,
                'genre': None
            }
            
        except Exception:
            return self._get_default_metadata()
    
    def _extract_mp3_metadata_manual(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extração manual básica de metadados MP3.
        """
        try:
            # Análise muito básica do cabeçalho MP3
            # Esta é uma implementação simplificada
            
            # Procurar por frame header MP3
            for i in range(len(audio_data) - 4):
                if audio_data[i] == 0xFF and (audio_data[i+1] & 0xE0) == 0xE0:
                    # Frame header encontrado
                    header = struct.unpack('>I', audio_data[i:i+4])[0]
                    
                    # Extrair informações do header (implementação básica)
                    version = (header >> 19) & 0x3
                    layer = (header >> 17) & 0x3
                    bitrate_index = (header >> 12) & 0xF
                    sample_rate_index = (header >> 10) & 0x3
                    channel_mode = (header >> 6) & 0x3
                    
                    # Mapear para valores reais (simplificado)
                    sample_rates = [44100, 48000, 32000, 0]
                    sample_rate = sample_rates[sample_rate_index] if sample_rate_index < 3 else None
                    
                    channels = 1 if channel_mode == 3 else 2
                    
                    return {
                        'duration_seconds': None,  # Difícil calcular sem análise completa
                        'bitrate': None,  # Difícil calcular sem análise completa
                        'sample_rate': sample_rate,
                        'channels': channels,
                        'genre': None
                    }
                    
            return self._get_default_metadata()
            
        except Exception:
            return self._get_default_metadata()
    
    def _get_default_metadata(self) -> Dict[str, Any]:
        """
        Retorna metadados padrão quando a extração falha.
        """
        return {
            'duration_seconds': None,
            'bitrate': None,
            'sample_rate': None,
            'channels': None,
            'genre': None
        }
    
    async def validate_audio_integrity(self, audio_data: bytes) -> bool:
        """
        Valida a integridade de um arquivo de áudio.
        """
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, self._validate_audio_integrity_sync, audio_data
            )
        except Exception:
            return False
    
    def _validate_audio_integrity_sync(self, audio_data: bytes) -> bool:
        """
        Validação síncrona de integridade de áudio.
        """
        try:
            audio_file_obj = io.BytesIO(audio_data)
            audiofile = mutagen.File(audio_file_obj)
            
            if audiofile is None:
                # Se Mutagen não conseguir carregar, tentar validação manual
                return self._validate_audio_manual(audio_data)
            
            # Se conseguiu carregar, arquivo é válido
            return True
            
        except Exception:
            return False
    
    def _validate_audio_manual(self, audio_data: bytes) -> bool:
        """
        Validação manual de integridade de áudio.
        """
        if len(audio_data) < 16:
            return False
        
        # Verificar cabeçalhos conhecidos
        format_from_header = self._detect_format_from_header(audio_data)
        return format_from_header is not None
    
    async def get_audio_duration(self, audio_data: bytes) -> Optional[float]:
        """
        Obtém a duração de um arquivo de áudio em segundos.
        """
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, self._get_audio_duration_sync, audio_data
            )
        except Exception:
            return None
    
    def _get_audio_duration_sync(self, audio_data: bytes) -> Optional[float]:
        """
        Obtenção síncrona da duração do áudio.
        """
        try:
            audio_file_obj = io.BytesIO(audio_data)
            audiofile = mutagen.File(audio_file_obj)
            
            if audiofile and hasattr(audiofile.info, 'length'):
                return float(audiofile.info.length)
            
            return None
            
        except Exception:
            return None
    
    async def extract_audio_properties(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extrai propriedades técnicas do áudio.
        """
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, self._extract_audio_properties_sync, audio_data
            )
        except Exception as e:
            raise ValueError(f"Erro ao extrair propriedades do áudio: {str(e)}")
    
    def _extract_audio_properties_sync(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extração síncrona de propriedades técnicas do áudio.
        """
        try:
            audio_file_obj = io.BytesIO(audio_data)
            audiofile = mutagen.File(audio_file_obj)
            
            if audiofile is None:
                return self._get_default_properties()
            
            info = audiofile.info
            
            bitrate = getattr(info, 'bitrate', None)
            sample_rate = getattr(info, 'sample_rate', None)
            channels = getattr(info, 'channels', None)
            
            # Determinar codec baseado no tipo de arquivo
            codec = type(audiofile).__name__
            
            # Determinar se é lossy
            is_lossy = isinstance(audiofile, (MP3, OggVorbis))
            
            # Calcular pontuação de qualidade
            quality_score = self._calculate_quality_score(bitrate, sample_rate, is_lossy)
            
            return {
                'bitrate': int(bitrate) if bitrate else None,
                'sample_rate': int(sample_rate) if sample_rate else None,
                'channels': int(channels) if channels else None,
                'codec': codec,
                'is_lossy': is_lossy,
                'quality_score': quality_score
            }
            
        except Exception:
            return self._get_default_properties()
    
    def _get_default_properties(self) -> Dict[str, Any]:
        """
        Retorna propriedades padrão quando a extração falha.
        """
        return {
            'bitrate': None,
            'sample_rate': None,
            'channels': None,
            'codec': 'unknown',
            'is_lossy': True,
            'quality_score': 0
        }
    
    def _calculate_quality_score(self, bitrate: Optional[int], sample_rate: Optional[int], 
                               is_lossy: bool) -> int:
        """
        Calcula uma pontuação de qualidade de 0-100 baseada nas propriedades do áudio.
        """
        if not bitrate or not sample_rate:
            return 0
        
        score = 0
        
        # Pontuação baseada no bitrate
        if is_lossy:
            if bitrate >= 320:
                score += 40
            elif bitrate >= 256:
                score += 35
            elif bitrate >= 192:
                score += 30
            elif bitrate >= 128:
                score += 25
            else:
                score += 15
        else:
            score += 45  # Lossless sempre tem pontuação alta
        
        # Pontuação baseada na taxa de amostragem
        if sample_rate >= 96000:
            score += 30
        elif sample_rate >= 48000:
            score += 25
        elif sample_rate >= 44100:
            score += 20
        else:
            score += 10
        
        # Pontuação baseada no tipo de compressão
        if not is_lossy:
            score += 25
        
        return min(score, 100)
    
    async def extract_id3_tags(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extrai tags ID3 de um arquivo de áudio.
        """
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, self._extract_id3_tags_sync, audio_data
            )
        except Exception as e:
            raise ValueError(f"Erro ao extrair tags ID3: {str(e)}")
    
    def _extract_id3_tags_sync(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extração síncrona de tags ID3.
        """
        try:
            audio_file_obj = io.BytesIO(audio_data)
            audiofile = mutagen.File(audio_file_obj)
            
            if audiofile is None or not audiofile.tags:
                return {}
            
            tags = {}
            
            # Campos comuns de tags
            tag_mapping = {
                'title': ['TIT2', 'TITLE', 'title'],
                'artist': ['TPE1', 'ARTIST', 'artist'],
                'album': ['TALB', 'ALBUM', 'album'],
                'date': ['TDRC', 'DATE', 'date'],
                'genre': ['TCON', 'GENRE', 'genre'],
                'track': ['TRCK', 'TRACKNUMBER', 'tracknumber'],
                'albumartist': ['TPE2', 'ALBUMARTIST', 'albumartist'],
                'composer': ['TCOM', 'COMPOSER', 'composer']
            }
            
            for field, possible_keys in tag_mapping.items():
                value = None
                for key in possible_keys:
                    if key in audiofile.tags:
                        tag_value = audiofile.tags[key]
                        if isinstance(tag_value, list) and len(tag_value) > 0:
                            value = str(tag_value[0])
                        elif isinstance(tag_value, str):
                            value = tag_value
                        break
                
                if value:
                    tags[field] = value
            
            return tags
            
        except Exception:
            return {}