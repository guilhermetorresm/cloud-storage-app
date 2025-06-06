import logging
from typing import Tuple

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.domain.value_objects import Email, Username, Password
from cloud_storage_app.domain.repositories.user_repository import UserRepository
from cloud_storage_app.application.dtos.user_dtos import CreateUserDTO, UserResponseDTO
from cloud_storage_app.infrastructure.auth.password_service import PasswordService
from cloud_storage_app.domain.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserValidationException,
    InvalidPasswordException
)

logger = logging.getLogger(__name__)


class CreateUserUseCase:
    """Use Case para criar um novo usuário"""

    @inject
    def __init__(
        self,
        user_repository: UserRepository = Provide["user_repository"],
        password_service: PasswordService = Provide["password_service"],
        db_session: AsyncSession = Provide["db_session"],
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._db_session = db_session

    async def _validate_user_data(self, create_user_dto: CreateUserDTO) -> None:
        """Valida os dados do usuário antes da criação."""
        # Verifica username
        if await self._user_repository.exists_by_username(Username(create_user_dto.username)):
            raise UserAlreadyExistsException(
                identifier=create_user_dto.username,
                identifier_type="username"
            )
        
        # Verifica email
        if await self._user_repository.exists_by_email(Email(create_user_dto.email)):
            raise UserAlreadyExistsException(
                identifier=create_user_dto.email,
                identifier_type="email"
            )

    async def execute(self, create_user_dto: CreateUserDTO) -> UserResponseDTO:
        """
        Este caso de uso é responsável por:
        1. Validar a unicidade do username e email
        2. Hashear a senha do usuário
        3. Criar a entidade User
        4. Persistir o usuário no banco de dados
        
        Attributes:
            _user_repository (UserRepository): Repositório para operações com usuários
            _password_service (PasswordService): Serviço para operações com senhas
            _db_session (AsyncSession): Sessão do banco de dados
        
        Args:
            create_user_dto: DTO com os dados do usuário a ser criado.
            
        Returns:
            UserResponseDTO: DTO com os dados do usuário criado.
            
        Raises:
            UserAlreadyExistsException: Se o email ou username já existirem.
            UserValidationException: Se houver erro de validação nos dados.
            InvalidPasswordException: Se a senha não atender aos requisitos.
        """
        logger.info(f"Iniciando criação de usuário para o email: {create_user_dto.email}")

        try:
            # 1. Validação dos dados
            await self._validate_user_data(create_user_dto)

            # 2. Processamento: Hashear a senha
            try:
                hashed_password = self._password_service.hash_password(Password(create_user_dto.password))
            except ValueError as e:
                raise InvalidPasswordException(str(e))

            # 3. Criação da entidade
            try:
                new_user = User.create(
                    username=create_user_dto.username,
                    email=create_user_dto.email,
                    hashed_password=hashed_password.value,
                    first_name=create_user_dto.first_name,
                    last_name=create_user_dto.last_name,
                )
            except ValueError as e:
                raise UserValidationException(str(e))

            # 4. Persistência
            await self._user_repository.save(new_user)
            await self._db_session.commit()
            
            logger.info(f"Usuário criado com sucesso: {new_user}")
            return UserResponseDTO.model_validate(new_user)

        except (UserAlreadyExistsException, UserValidationException, InvalidPasswordException) as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            await self._db_session.rollback()
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar usuário: {str(e)}")
            await self._db_session.rollback()
            raise
