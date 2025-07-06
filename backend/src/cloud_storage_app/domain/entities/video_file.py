from dataclasses import dataclass, field
from typing import Optional, List, Dict
from .base_file import BaseFile
from ..value_objects import Tag, VideoVersion, FilePath


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

    _thumbnail: Optional[FilePath] = None
    
    # Gerenciamento de versões do vídeo
    _versions: Dict[str, VideoVersion] = field(default_factory=dict)
    _original_version: Optional[str] = None
    
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
                created_with: Optional[str] = None, genre: Optional[str] = None,
                thumbnail_path: Optional[str] = None, original_resolution: Optional[str] = None) -> "VideoFile":
        """Cria um novo arquivo de vídeo"""
        tags_list = [Tag(tag) for tag in tags]
        
        # Criar thumbnail se fornecido
        thumbnail_entity = None
        if thumbnail_path:
            thumbnail_entity = FilePath(thumbnail_path)
        
        video_file = super().create(
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
            _genre=genre,
            _thumbnail=thumbnail_entity
        )
        
        # Se foi especificada uma resolução original, cria a versão correspondente
        if original_resolution:
            from ..value_objects import FilePath
            import uuid
            from datetime import date
            
            # Cria o caminho para a versão original
            original_path = FilePath.create_video(
                user_id=uuid.UUID(str(owner_id)),
                file_id=str(video_file.file_id),
                resolution=original_resolution,
                file_name=name,
                file_date=date.today()
            )
            
            # Cria a versão original
            original_version = VideoVersion(
                resolution=original_resolution,
                file_path=original_path,
                is_original=True,
                processing_status="completed"  # Versão original já está pronta
            )
            
            video_file.add_version(original_version)
        
        return video_file
    
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
            'created_with': self._created_with,
            'versions': {
                resolution: {
                    'file_path': str(version.file_path),
                    'is_original': version.is_original,
                    'processing_status': version.processing_status,
                    'is_ready': version.is_ready
                }
                for resolution, version in self._versions.items()
            },
            'versions_count': self.versions_count,
            'original_version': self._original_version,
            'available_resolutions': self.get_available_versions(),
            'thumbnail': {
                'has_thumbnail': self.has_thumbnail,
                'path': str(self._thumbnail) if self._thumbnail else None
            }
        }
    
    def is_valid_file_type(self) -> bool:
        """Verifica se o tipo de arquivo é válido para vídeo"""
        return self._file_type.is_video
    
    # Métodos para gerenciamento de versões
    def add_version(self, version: VideoVersion) -> None:
        """Adiciona uma nova versão do vídeo"""
        if version.resolution in self._versions:
            raise ValueError(f"Versão com resolução {version.resolution} já existe")
        
        self._versions[version.resolution] = version
        
        # Se for a versão original, marca como tal
        if version.is_original:
            self._original_version = version.resolution
        
        self._mark_as_updated()
    
    def remove_version(self, resolution: str) -> None:
        """Remove uma versão específica do vídeo"""
        if resolution not in self._versions:
            raise ValueError(f"Versão com resolução {resolution} não existe")
        
        # Não permite remover a versão original
        if resolution == self._original_version:
            raise ValueError("Não é possível remover a versão original")
        
        del self._versions[resolution]
        self._mark_as_updated()
    
    def get_version(self, resolution: str) -> Optional[VideoVersion]:
        """Retorna uma versão específica do vídeo"""
        return self._versions.get(resolution)
    
    def get_original_version(self) -> Optional[VideoVersion]:
        """Retorna a versão original do vídeo"""
        if self._original_version:
            return self._versions.get(self._original_version)
        return None
    
    def get_available_versions(self) -> List[str]:
        """Retorna lista de resoluções disponíveis"""
        return list(self._versions.keys())
    
    def get_ready_versions(self) -> List[VideoVersion]:
        """Retorna apenas as versões que estão prontas para uso"""
        return [version for version in self._versions.values() if version.is_ready]
    
    def get_processing_versions(self) -> List[VideoVersion]:
        """Retorna versões que estão sendo processadas"""
        return [version for version in self._versions.values() if version.is_processing]
    
    def get_failed_versions(self) -> List[VideoVersion]:
        """Retorna versões que falharam no processamento"""
        return [version for version in self._versions.values() if version.has_failed]
    
    def update_version_status(self, resolution: str, status: str) -> None:
        """Atualiza o status de processamento de uma versão"""
        if resolution not in self._versions:
            raise ValueError(f"Versão com resolução {resolution} não existe")
        
        # Cria uma nova instância com o status atualizado
        current_version = self._versions[resolution]
        updated_version = VideoVersion(
            resolution=current_version.resolution,
            file_path=current_version.file_path,
            is_original=current_version.is_original,
            processing_status=status
        )
        
        self._versions[resolution] = updated_version
        self._mark_as_updated()
    
    def get_best_available_version(self, max_resolution: Optional[str] = None) -> Optional[VideoVersion]:
        """
        Retorna a melhor versão disponível baseada na resolução máxima desejada.
        
        Args:
            max_resolution: Resolução máxima desejada (ex: "1080p"). Se None, retorna a melhor disponível.
        """
        ready_versions = self.get_ready_versions()
        if not ready_versions:
            return None
        
        # Se não especificou resolução máxima, retorna a de maior qualidade
        if not max_resolution:
            return max(ready_versions, key=lambda v: v.height or 0)
        
        # Filtra versões até a resolução máxima
        max_height = VideoVersion(max_resolution, None).height
        available_versions = [v for v in ready_versions if v.height and v.height <= max_height]
        
        if not available_versions:
            return None
        
        # Retorna a de maior qualidade dentro do limite
        return max(available_versions, key=lambda v: v.height or 0)
    
    @property
    def versions_count(self) -> int:
        """Retorna o número total de versões"""
        return len(self._versions)
    
    @property
    def has_versions(self) -> bool:
        """Verifica se o vídeo tem versões"""
        return len(self._versions) > 0
    
    # Métodos para gerenciamento de thumbnails
    @property
    def thumbnail(self) -> Optional[FilePath]:
        """Retorna o caminho do thumbnail do vídeo"""
        return self._thumbnail
    
    @property
    def has_thumbnail(self) -> bool:
        """Verifica se o vídeo tem thumbnail"""
        return self._thumbnail is not None
    
    def set_thumbnail(self, thumbnail_path: str) -> None:
        """Define o thumbnail do vídeo"""
        self._thumbnail = FilePath(thumbnail_path)
        self._mark_as_updated()
    
    def remove_thumbnail(self) -> None:
        """Remove o thumbnail do vídeo"""
        self._thumbnail = None
        self._mark_as_updated()
    
    def generate_thumbnail_path(self) -> FilePath:
        """Gera o caminho padrão para o thumbnail do vídeo"""
        import uuid
        from datetime import date
        
        return FilePath.create_thumbnail(
            user_id=uuid.UUID(str(self._owner_id)),
            file_id=str(self._file_id),
            file_name=self._name.value,
            file_type="videos",
            file_date=date.today()
        )