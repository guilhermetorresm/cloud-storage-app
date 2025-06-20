"""
Caso de uso para atualizar dados do usuário autenticado.
Responsável por validar token JWT e atualizar informações do usuário.
"""

import logging
from typing import Optional
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
from cloud_storage_app.domain.value_objects.user_id import UserId
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService, TokenPayload
from cloud_storage_app.application.dtos.user_dtos import UserResponseDTO, UpdateUserDTO
from cloud_storage_app.application.exceptions import (
    AuthenticationException,
    UserNotFoundException,
    ValidationException
)
from cloud_storage_app.infrastructure.auth import (
    InvalidTokenException,
    ExpiredTokenException,
    JWTException
)
from cloud_storage_app.domain.value_objects import Username, FirstName, LastName, UserDescription
from cloud_storage_app.domain.exceptions.user_exceptions import UserAlreadyExistsException

logger = logging.getLogger(__name__)


class UpdateUserUseCase:
    """
    Caso de uso para atualizar dados do usuário autenticado.
    
    Responsabilidades:
    - Decodificar e validar token JWT
    - Validar dados de atualização
    - Atualizar dados do usuário no repositório
    - Retornar dados atualizados do usuário
    - Tratar erros de token inválido ou expirado
    """
    
    @inject
    def __init__(
        self,
        jwt_service: JWTService,
    ):
        self._jwt_service = jwt_service
        self._db_session = None  # Será definida no execute()
        self._user_repository = None  # Será criada no execute()
        logger.debug("UpdateUserUseCase inicializado")
    
    async def execute(self, request: UpdateUserDTO, access_token: str, db_session: AsyncSession) -> UserResponseDTO:
        """
        Executa o caso de uso para atualizar dados do usuário.
        
        Args:
            request: UpdateUserDTO contendo dados para atualização
            access_token: Token JWT de acesso
            db_session: Sessão do banco de dados
            
        Returns:
            UserResponseDTO: Dados atualizados do usuário
            
        Raises:
            AuthenticationException: Se o token for inválido, expirado ou usuário não encontrado
            ValidationException: Se os dados de atualização forem inválidos
        """
        self._db_session = db_session
        self._user_repository = UserRepository(session=db_session)

        try:
            logger.debug("Iniciando processo de atualização do usuário")
            
            # 1. Validar entrada
            self._validate_request(request, access_token)
            
            # 2. Decodificar e validar token JWT
            token_payload = await self._decode_and_validate_token(access_token)
            
            # 3. Buscar usuário no repositório
            user = await self._find_user_by_id(token_payload.sub)
            
            # 4. Verificar status do usuário
            self._check_user_status(user)
            
            # 5. Atualizar dados do usuário
            updated_user = await self._update_user_data(user, request)
            
            # 6. Converter para DTO e retornar
            user_response = self._convert_to_dto(updated_user)
            
            logger.info(f"Dados do usuário atualizados com sucesso: {user.username.value}")
            return user_response
            
        except (AuthenticationException, UserNotFoundException, ValidationException):
            # Re-raise exceções conhecidas
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar usuário: {str(e)}")
            logger.debug(f"Detalhes do erro: {e.__class__.__name__}: {str(e)}")
            raise AuthenticationException("Erro interno ao atualizar dados do usuário") from e
    
    def _validate_request(self, request: UpdateUserDTO, access_token: str) -> None:
        """
        Valida os dados de entrada do request.
        
        Args:
            request: Request com dados para atualização
            access_token: Token JWT de acesso
            
        Raises:
            AuthenticationException: Se o token estiver inválido
            ValidationException: Se os dados de atualização forem inválidos
        """
        if not access_token or not access_token.strip():
            logger.warning("Token de acesso não fornecido")
            raise AuthenticationException("Token de acesso é obrigatório")
        
        # Verificar formato básico do token
        token_parts = access_token.strip().split('.')
        if len(token_parts) != 3:
            logger.warning("Token de acesso com formato inválido")
            raise AuthenticationException("Formato de token inválido")
        
        # Validar dados de atualização
        if not request.first_name and not request.last_name and not request.username and not request.description:
            logger.warning("Nenhum dado para atualização fornecido")
            raise ValidationException("Pelo menos um campo deve ser fornecido para atualização")
    
    async def _decode_and_validate_token(self, access_token: str) -> TokenPayload:
        """
        Decodifica e valida o token JWT.
        
        Args:
            access_token: Token JWT de acesso
            
        Returns:
            TokenPayload: Payload decodificado do token
            
        Raises:
            AuthenticationException: Se o token for inválido ou expirado
        """
        try:
            logger.debug("Decodificando token JWT")
            
            # Decodificar token
            token_payload = self._jwt_service.decode_token(access_token)
            
            # Validar se é um access token
            if not self._jwt_service.validate_token_type(token_payload, "access"):
                logger.warning("Token fornecido não é um access token")
                raise AuthenticationException("Tipo de token inválido")
            
            logger.debug(f"Token decodificado com sucesso para usuário: {token_payload.sub}")
            return token_payload
            
        except ExpiredTokenException as e:
            logger.warning(f"Token expirado: {str(e)}")
            raise AuthenticationException("Token expirado") from e
            
        except InvalidTokenException as e:
            logger.warning(f"Token inválido: {str(e)}")
            raise AuthenticationException("Token inválido") from e
            
        except JWTException as e:
            logger.error(f"Erro JWT: {str(e)}")
            raise AuthenticationException("Erro ao processar token") from e
            
        except Exception as e:
            logger.error(f"Erro inesperado ao decodificar token: {str(e)}")
            raise AuthenticationException("Erro interno ao processar token") from e
    
    
    async def _find_user_by_id(self, user_id_str: str) -> User:
        """
        Busca usuário pelo ID extraído do token.
        
        Args:
            user_id_str: String do ID do usuário
            
        Returns:
            User: Entidade do usuário encontrado
            
        Raises:
            UserNotFoundException: Se o usuário não for encontrado
            AuthenticationException: Para outros erros de busca
        """
        try:
            logger.info(f"Buscando usuário por ID: {user_id_str}")
            
            user_id = UserId.from_string(user_id_str)
            user = await self._user_repository.find_by_id(user_id)
            
            if not user:
                logger.warning(f"Usuário não encontrado para ID: {user_id_str}")
                raise UserNotFoundException("Usuário não encontrado")
            
            logger.debug(f"Usuário encontrado: {user.username.value}")
            return user
            
        except UserNotFoundException:
            raise
        except ValueError as e:
            logger.error(f"ID de usuário inválido: {str(e)}")
            raise AuthenticationException("ID de usuário inválido no token") from e
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {str(e)}")
            raise AuthenticationException("Erro ao buscar dados do usuário") from e
    
    def _check_user_status(self, user: User) -> None:
        """
        Verifica se o usuário está em status válido.
        
        Args:
            user: Entidade do usuário
            
        Raises:
            AuthenticationException: Se o usuário não puder ser autenticado
        """
        if not user:
            raise AuthenticationException("Status de usuário inválido")
        
        if hasattr(user, 'is_active') and not user.is_active:
            logger.warning(f"Tentativa de atualização com usuário inativo: {user.username.value}")
            raise AuthenticationException("Usuário inativo")
        
        logger.debug(f"Status do usuário {user.username.value} verificado com sucesso")
    
    async def _update_user_data(self, user: User, request: UpdateUserDTO) -> User:
        """
        Atualiza os dados do usuário com as informações fornecidas.
        
        Args:
            user: Entidade do usuário atual
            request: DTO com dados para atualização
            
        Returns:
            User: Entidade do usuário atualizada
            
        Raises:
            ValidationException: Se houver erro na atualização
            UserAlreadyExistsException: Se o novo username já estiver em uso
        """
        try:
            logger.debug(f"Iniciando atualização dos dados do usuário: {user.username.value}")
            
            logger.info(f"Atualizando dados do usuário com request:\n{request}")
            
            # Atualizar dados usando o método update_profile
            logger.info(f"Dados do usuário atual obtidos:\n{user}")
            user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                description=request.description
            )
            logger.info(f"Dados do usuário atualizados:\n{user}")
            
            # Se username for fornecido, validar e atualizar
            if request.username:
                # Verificar se o novo username é diferente do atual
                if request.username != user.username.value:
                    # Verificar se o novo username já está em uso
                    new_username = Username(request.username)
                    username_exists = await self._user_repository.exists_by_username(new_username)
                    
                    if username_exists:
                        logger.warning(f"Tentativa de atualizar para username já existente: {request.username}")
                        raise UserAlreadyExistsException(
                            identifier=request.username,
                            identifier_type="username"
                        )
                    
                    # Atualizar username
                    user._username = new_username
            

            logger.info(f"Dados do usuário atualizados:\n{user}")
            
            # Salvar alterações no repositório
            await self._user_repository.save(user)
            
            # Buscar usuário atualizado
            updated_user = await self._user_repository.find_by_id(user.user_id)
            if not updated_user:
                raise ValidationException("Erro ao buscar usuário após atualização")
            
            logger.info(f"Dados do usuário atualizados com sucesso: {user.username.value}")
            return updated_user
            
        except UserAlreadyExistsException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar dados do usuário: {str(e)}")
            raise ValidationException("Erro ao atualizar dados do usuário") from e
    
    def _convert_to_dto(self, user: User) -> UserResponseDTO:
        """
        Converte entidade User para DTO de resposta.
        
        Args:
            user: Entidade do usuário
            
        Returns:
            UserResponseDTO: DTO com dados do usuário
        """
        try:
            return UserResponseDTO(
                user_id=str(user.user_id.value),
                username=user.username.value,
                first_name=user.first_name.value,
                last_name=user.last_name.value if user.last_name else None,
                email=user.email.value,
                profile_picture=user.profile_picture.value if user.profile_picture else None,
                description=user.description.value if user.description else None,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
                is_active=user.is_active
            )
        except Exception as e:
            logger.error(f"Erro ao converter usuário para DTO: {str(e)}")
            raise AuthenticationException("Erro ao processar dados do usuário") from e 