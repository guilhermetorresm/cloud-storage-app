from abc import ABC, abstractmethod
from typing import Optional, List
from cloud_storage_app.domain.entities import VideoFile
from cloud_storage_app.domain.value_objects import FileId, UserId


class VideoFileRepositoryInterface(ABC):
    """
    Interface do repositório de arquivos de vídeo (Domain Layer).
    """
    
    @abstractmethod
    async def save(self, video_file: VideoFile) -> None:
        """Salva ou atualiza um arquivo de vídeo."""
        pass
    
    @abstractmethod
    async def find_by_id(self, file_id: FileId) -> Optional[VideoFile]:
        """Busca um arquivo de vídeo por ID."""
        pass
    
    @abstractmethod
    async def find_by_owner_id(self, owner_id: UserId) -> List[VideoFile]:
        """Busca arquivos por proprietário."""
        pass
    
    @abstractmethod
    async def find_by_name_and_owner(self, name: str, owner_id: UserId) -> Optional[VideoFile]:
        """Busca arquivo por nome e proprietário."""
        pass
    
    @abstractmethod
    async def find_by_tags(self, tags: List[str], owner_id: UserId) -> List[VideoFile]:
        """Busca arquivos por tags."""
        pass
    
    @abstractmethod
    async def find_by_duration_range(self, min_duration: int, max_duration: int, owner_id: UserId) -> List[VideoFile]:
        """Busca vídeos por faixa de duração."""
        pass
    
    @abstractmethod
    async def find_by_resolution(self, resolution: str, owner_id: UserId) -> List[VideoFile]:
        """Busca vídeos por resolução."""
        pass
    
    @abstractmethod
    async def find_by_codec(self, codec: str, owner_id: UserId) -> List[VideoFile]:
        """Busca vídeos por codec."""
        pass
    
    @abstractmethod
    async def delete(self, file_id: FileId) -> None:
        """Remove um arquivo (soft delete)."""
        pass
    
    @abstractmethod
    async def find_all_active(self, limit: int = 100, offset: int = 0) -> List[VideoFile]:
        """Lista arquivos ativos com paginação."""
        pass