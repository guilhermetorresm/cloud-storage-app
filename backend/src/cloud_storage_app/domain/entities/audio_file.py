from dataclasses import dataclass
from typing import Optional, List
from .base_file import BaseFile
from ..value_objects import FileType, FileTypeEnum
from ..value_objects import Tag


@dataclass
class AudioFile(BaseFile):
    """
    Entidade para arquivos de áudio.
    
    Estende BaseFile com metadados específicos de áudio.
    """
    
    # Metadados específicos de áudio
    _duration_seconds: Optional[int] = None
    _bitrate: Optional[int] = None
    _sample_rate: Optional[int] = None
    _channels: Optional[int] = None
    _genre: Optional[str] = None
    
    def __post_init__(self):
        """Validações específicas de áudio"""
        super().__post_init__()
        
        if not self.is_valid_file_type():
            raise ValueError("Tipo de arquivo inválido para AudioFile")
    
    @classmethod
    def create(cls, owner_id, name: str, path: str, size: int, 
               description: str, tags: List[str], duration_seconds: Optional[int] = None,
               bitrate: Optional[int] = None, sample_rate: Optional[int] = None,
               channels: Optional[int] = None, genre: Optional[str] = None) -> "AudioFile":
        """Cria um novo arquivo de áudio"""
        tags_list = [Tag(tag) for tag in tags]
        return super().create(
            owner_id=owner_id,
            name=name,
            path=path,
            size=size,
            description=description,
            tags=tags_list,
            _duration_seconds=duration_seconds,
            _bitrate=bitrate,
            _sample_rate=sample_rate,
            _channels=channels,
            _genre=genre,
        )
    
    # Getters para metadados de áudio
    @property
    def duration_seconds(self) -> Optional[int]:
        return self._duration_seconds
    
    @property
    def bitrate(self) -> Optional[int]:
        return self._bitrate
    
    @property
    def sample_rate(self) -> Optional[int]:
        return self._sample_rate
    
    @property
    def channels(self) -> Optional[int]:
        return self._channels
    
    @property
    def genre(self) -> Optional[str]:
        return self._genre
    
    @property
    def duration_formatted(self) -> str:
        """Retorna a duração formatada em MM:SS"""
        if self._duration_seconds is None:
            return "Desconhecido"
        
        minutes = self._duration_seconds // 60
        seconds = self._duration_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    # Métodos de domínio específicos
    def update_metadata(self, duration_seconds: Optional[int] = None,
                       bitrate: Optional[int] = None,
                       sample_rate: Optional[int] = None,
                       channels: Optional[int] = None,
                       genre: Optional[str] = None) -> None:
        """Atualiza os metadados do arquivo de áudio"""
        if duration_seconds is not None:
            self._duration_seconds = duration_seconds
        if bitrate is not None:
            self._bitrate = bitrate
        if sample_rate is not None:
            self._sample_rate = sample_rate
        if channels is not None:
            self._channels = channels
        if genre is not None:
            self._genre = genre
        
        self._mark_as_updated()
    
    def get_metadata(self) -> dict:
        """Retorna metadados específicos do arquivo de áudio"""
        return {
            'duration_seconds': self._duration_seconds,
            'duration_formatted': self.duration_formatted,
            'bitrate': self._bitrate,
            'sample_rate': self._sample_rate,
            'channels': self._channels,
            'genre': self._genre,
        }
    
    def is_valid_file_type(self) -> bool:
        """Verifica se o tipo de arquivo é válido para áudio"""
        return self._file_type.is_audio