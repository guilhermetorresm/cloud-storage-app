from abc import ABC, abstractmethod
from typing import Optional, List
from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.domain.value_objects.user_id import UserId
from cloud_storage_app.domain.value_objects.email import Email
from cloud_storage_app.domain.value_objects.username import Username


class UserRepository(ABC):
    """
    Interface do repositório de usuários (Domain Layer).
    """
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """Salva ou atualiza um usuário."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Busca usuário por ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Busca usuário por email."""
        pass
    
    @abstractmethod
    async def find_by_username(self, username: Username) -> Optional[User]:
        """Busca usuário por username."""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Verifica se existe usuário com o email."""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: Username) -> bool:
        """Verifica se existe usuário com o username."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Remove um usuário, nesse caso apenas desativa o usuário."""
        pass
    
    @abstractmethod
    async def find_all_active(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Lista usuários ativos com paginação."""
        pass
