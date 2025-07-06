from abc import ABC, abstractmethod
from typing import Optional, List
from cloud_storage_app.domain.entities import ImageFile
from cloud_storage_app.domain.value_objects import FileId, UserId


class ImageFileRepositoryInterface(ABC):
    """
    Interface do repositório de arquivos de imagem (Domain Layer).
    """
    
    @abstractmethod
    async def save(self, image_file: ImageFile) -> None:
        """Salva ou atualiza um arquivo de imagem."""
        pass
    
    @abstractmethod
    async def find_by_id(self, file_id: FileId) -> Optional[ImageFile]:
        """Busca um arquivo de imagem por ID."""
        pass
    
    @abstractmethod
    async def find_by_owner_id(self, owner_id: UserId) -> List[ImageFile]:
        """Busca arquivos por proprietário."""
        pass
    
    @abstractmethod
    async def find_by_name_and_owner(self, name: str, owner_id: UserId) -> Optional[ImageFile]:
        """Busca arquivo por nome e proprietário."""
        pass
    
    @abstractmethod
    async def find_by_tags(self, tags: List[str], owner_id: UserId) -> List[ImageFile]:
        """Busca arquivos por tags."""
        pass
    
    @abstractmethod
    async def delete(self, file_id: FileId) -> None:
        """Remove um arquivo (soft delete)."""
        pass
    
    @abstractmethod
    async def find_all_active(self, limit: int = 100, offset: int = 0) -> List[ImageFile]:
        """Lista arquivos ativos com paginação."""
        pass