from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from cloud_storage_app.domain.repositories.user_repository import UserRepository as UserRepositoryInterface
from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.domain.value_objects.user_id import UserId
from cloud_storage_app.domain.value_objects.email import Email
from cloud_storage_app.domain.value_objects.username import Username
from cloud_storage_app.infrastructure.database.models.user_model import UserModel


class UserRepository(UserRepositoryInterface):
    """
    Implementação concreta do repositório de usuários.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> None:
        """Salva ou atualiza um usuário."""
        # Buscar se já existe no banco
        existing_model = await self._session.get(UserModel, user.user_id.value)
        
        if existing_model:
            # Atualizar usuário existente
            existing_model.username = user.username.value
            existing_model.email = user.email.value
            existing_model.first_name = user.first_name.value
            existing_model.last_name = user.last_name.value if user.last_name else None
            existing_model.profile_picture = user.profile_picture.value if user.profile_picture else None
            existing_model.description = user.description.value if user.description else None
            existing_model.is_active = user.is_active
            existing_model.updated_at = user.updated_at
            existing_model.last_login_at = user.last_login_at
        else:
            # Criar novo usuário
            user_model = UserModel(
                id=user.user_id.value,
                username=user.username.value,
                email=user.email.value,
                hashed_password=user._hashed_password.value,
                first_name=user.first_name.value,
                last_name=user.last_name.value if user.last_name else None,
                profile_picture=user.profile_picture.value if user.profile_picture else None,
                description=user.description.value if user.description else None,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at
            )
            self._session.add(user_model)
        
        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            raise ValueError(f"Erro ao salvar usuário: {str(e)}")

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Busca usuário por ID."""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None

    async def find_by_email(self, email: Email) -> Optional[User]:
        """Busca usuário por email."""
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None

    async def find_by_username(self, username: Username) -> Optional[User]:
        """Busca usuário por username."""
        stmt = select(UserModel).where(UserModel.username == username.value)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._model_to_entity(user_model)
        return None

    async def exists_by_email(self, email: Email) -> bool:
        """Verifica se existe usuário com o email."""
        stmt = select(UserModel.id).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: Username) -> bool:
        """Verifica se existe usuário com o username."""
        stmt = select(UserModel.id).where(UserModel.username == username.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete(self, user_id: UserId) -> None:
        """Remove um usuário (desativa)."""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id.value)
            .values(is_active=False)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def find_all_active(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Lista usuários ativos com paginação."""
        stmt = (
            select(UserModel)
            .where(UserModel.is_active == True)
            .offset(offset)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in user_models]

    def _model_to_entity(self, model: UserModel) -> User:
        """Converte UserModel para User entity."""
        from cloud_storage_app.domain.value_objects import (
            UserId, Username, Email, HashedPassword, FirstName, LastName,
            ProfilePicture, UserDescription
        )
        
        # Criar instância User diretamente com os atributos privados
        user = User.__new__(User)  # Criar sem chamar __init__
        
        # Definir atributos privados diretamente
        user._user_id = UserId(model.id)
        user._username = Username(model.username)
        user._email = Email(model.email)
        user._hashed_password = HashedPassword(model.hashed_password)
        user._first_name = FirstName(model.first_name)
        user._last_name = LastName(model.last_name) if model.last_name else None
        user._profile_picture = ProfilePicture(model.profile_picture) if model.profile_picture else None
        user._description = UserDescription(model.description) if model.description else None
        user._is_active = model.is_active
        user._created_at = model.created_at
        user._updated_at = model.updated_at
        user._last_login_at = model.last_login_at
        user._domain_events = []
        
        return user