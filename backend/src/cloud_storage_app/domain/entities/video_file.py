from dataclasses import dataclass
from typing import Optional, List
from .base_file import BaseFile
from ..value_objects import Tag


@dataclass
class VideoFile(BaseFile):
    """
    Entidade para arquivos de vídeo.
    
    Estende BaseFile com metadados específicos de vídeo.
    """
    
    # Metadados específicos de vídeo
    _duration_seconds: Optional[int] = None
    _width: Optional[int] = None
    _height: Optional[int] = None
    _frame_rate: Optional[float] = None
    _bitrate: Optional[int] = None
    _codec: Optional[str] = None
    _audio_codec: Optional[str] = None
    _has_audio: Optional[bool] = None
    _has_subtitles: Optional[bool] = None
    _created_with: Optional[str] = None  # Software usado para criar o vídeo
    _genre: Optional[str] = None
    
    def __post_init__(self):
        """Validações específicas de vídeo"""
        super().__post_init__()
        
        if not self.is_valid_file_type():
            raise ValueError("Tipo de arquivo inválido para VideoFile")
    
    @classmethod
    def create(cls, owner_id, name: str, path: str, size: int, 
               description: str, tags: List[str], duration_seconds: Optional[int] = None,
               width: Optional[int] = None, height: Optional[int] = None,
               frame_rate: Optional[float] = None, bitrate: Optional[int] = None,
               codec: Optional[str] = None, audio_codec: Optional[str] = None,
               has_audio: Optional[bool] = None, has_subtitles: Optional[bool] = None,
               created_with: Optional[str] = None, genre: Optional[str] = None) -> "VideoFile":
        """Cria um novo arquivo de vídeo"""
        tags_list = [Tag(tag) for tag in tags]
        return super().create(
            owner_id=owner_id,
            name=name,
            path=path,
            size=size,
            description=description,
            tags=tags_list,
            _duration_seconds=duration_seconds,
            _width=width,
            _height=height,
            _frame_rate=frame_rate,
            _bitrate=bitrate,
            _codec=codec,
            _audio_codec=audio_codec,
            _has_audio=has_audio,
            _has_subtitles=has_subtitles,
            _created_with=created_with,
            _genre=genre
        )
    
    # Getters para metadados de vídeo
    @property
    def duration_seconds(self) -> Optional[int]:
        return self._duration_seconds
    
    @property
    def width(self) -> Optional[int]:
        return self._width
    
    @property
    def height(self) -> Optional[int]:
        return self._height
    
    @property
    def frame_rate(self) -> Optional[float]:
        return self._frame_rate
    
    @property
    def bitrate(self) -> Optional[int]:
        return self._bitrate
    
    @property
    def codec(self) -> Optional[str]:
        return self._codec
    
    @property
    def audio_codec(self) -> Optional[str]:
        return self._audio_codec
    
    @property
    def has_audio(self) -> Optional[bool]:
        return self._has_audio
    
    @property
    def has_subtitles(self) -> Optional[bool]:
        return self._has_subtitles
    
    @property
    def created_with(self) -> Optional[str]:
        return self._created_with
    
    @property
    def duration_formatted(self) -> str:
        """Retorna a duração formatada em HH:MM:SS"""
        if self._duration_seconds is None:
            return "Desconhecido"
        
        hours = self._duration_seconds // 3600
        minutes = (self._duration_seconds % 3600) // 60
        seconds = self._duration_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def resolution(self) -> str:
        """Retorna a resolução formatada"""
        if self._width is None or self._height is None:
            return "Desconhecido"
        return f"{self._width}x{self._height}"
    
    @property
    def aspect_ratio(self) -> Optional[float]:
        """Retorna a proporção do vídeo"""
        if self._width is None or self._height is None or self._height == 0:
            return None
        return self._width / self._height
    
    @property
    def quality_level(self) -> str:
        """Retorna o nível de qualidade baseado na resolução"""
        if self._height is None:
            return "Desconhecido"
        
        if self._height >= 2160:
            return "4K/UHD"
        elif self._height >= 1440:
            return "2K/QHD"
        elif self._height >= 1080:
            return "Full HD"
        elif self._height >= 720:
            return "HD"
        elif self._height >= 480:
            return "SD"
        else:
            return "Baixa qualidade"
    
    @property
    def estimated_frames(self) -> Optional[int]:
        """Retorna o número estimado de frames"""
        if self._duration_seconds is None or self._frame_rate is None:
            return None
        return int(self._duration_seconds * self._frame_rate)
    
    # Métodos de domínio específicos
    def update_metadata(self, duration_seconds: Optional[int] = None,
                       width: Optional[int] = None, height: Optional[int] = None,
                       frame_rate: Optional[float] = None,
                       bitrate: Optional[int] = None,
                       codec: Optional[str] = None,
                       audio_codec: Optional[str] = None,
                       has_audio: Optional[bool] = None,
                       has_subtitles: Optional[bool] = None,
                       created_with: Optional[str] = None) -> None:
        """Atualiza os metadados do arquivo de vídeo"""
        if duration_seconds is not None:
            self._duration_seconds = duration_seconds
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height
        if frame_rate is not None:
            self._frame_rate = frame_rate
        if bitrate is not None:
            self._bitrate = bitrate
        if codec is not None:
            self._codec = codec
        if audio_codec is not None:
            self._audio_codec = audio_codec
        if has_audio is not None:
            self._has_audio = has_audio
        if has_subtitles is not None:
            self._has_subtitles = has_subtitles
        if created_with is not None:
            self._created_with = created_with
        
        self._mark_as_updated()
    
    def get_metadata(self) -> dict:
        """Retorna metadados específicos do arquivo de vídeo"""
        return {
            'duration_seconds': self._duration_seconds,
            'duration_formatted': self.duration_formatted,
            'width': self._width,
            'height': self._height,
            'resolution': self.resolution,
            'aspect_ratio': self.aspect_ratio,
            'quality_level': self.quality_level,
            'frame_rate': self._frame_rate,
            'estimated_frames': self.estimated_frames,
            'bitrate': self._bitrate,
            'codec': self._codec,
            'audio_codec': self._audio_codec,
            'has_audio': self._has_audio,
            'has_subtitles': self._has_subtitles,
            'created_with': self._created_with
        }
    
    def is_valid_file_type(self) -> bool:
        """Verifica se o tipo de arquivo é válido para vídeo"""
        return self._file_type.is_video