"""
Caso de uso para obter dados do usuário atual autenticado.
Responsável por decodificar token JWT e retornar informações do usuário.
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
from cloud_storage_app.application.dtos.user_dtos import UserResponseDTO, GetUsersMeDTO
from cloud_storage_app.application.exceptions import (
    AuthenticationException,
    UserNotFoundException
)
from cloud_storage_app.infrastructure.auth import (
    InvalidTokenException,
    ExpiredTokenException,
    JWTException
)

logger = logging.getLogger(__name__)


class GetCurrentUserUseCase:
    """
    Caso de uso para obter dados do usuário atual autenticado.
    
    Responsabilidades:
    - Decodificar e validar token JWT
    - Buscar dados completos do usuário no repositório
    - Retornar informações do usuário autenticado
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
        logger.debug("GetCurrentUserUseCase inicializado")
    
    async def execute(self, request: GetUsersMeDTO, db_session: AsyncSession) -> UserResponseDTO:
        """
        Executa o caso de uso para obter usuário atual.
        
        Args:
            request: GetCurrentUserRequest contendo o token de acesso
            
        Returns:
            UserResponseDTO: Dados completos do usuário autenticado
            
        Raises:
            AuthenticationException: Se o token for inválido, expirado ou usuário não encontrado
        """
        self._db_session = db_session
        self._user_repository = UserRepository(session=db_session)

        try:
            logger.debug("Iniciando processo de obtenção do usuário atual")
            
            # 1. Validar entrada
            self._validate_request(request)
            
            # 2. Decodificar e validar token JWT
            token_payload = await self._decode_and_validate_token(request.access_token)
            
            # 3. Buscar usuário no repositório
            user = await self._find_user_by_id(token_payload.sub)
            
            # 4. Verificar status do usuário
            self._check_user_status(user)
            
            # 5. Converter para DTO e retornar
            user_response = self._convert_to_dto(user)
            
            logger.info(f"Dados do usuário atual obtidos com sucesso: {user.username.value}")
            return user_response
            
        except (AuthenticationException, UserNotFoundException):
            # Re-raise exceções conhecidas
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao obter usuário atual: {str(e)}")
            logger.debug(f"Detalhes do erro: {e.__class__.__name__}: {str(e)}")
            raise AuthenticationException("Erro interno ao obter dados do usuário") from e
    
    def _validate_request(self, request: GetUsersMeDTO) -> None:
        """
        Valida os dados de entrada do request.
        
        Args:
            request: Request com token de acesso
            
        Raises:
            AuthenticationException: Se os dados estiverem inválidos
        """
        if not request.access_token or not request.access_token.strip():
            logger.warning("Token de acesso não fornecido")
            raise AuthenticationException("Token de acesso é obrigatório")
        
        # Verificar formato básico do token (deve ter 3 partes separadas por pontos)
        token_parts = request.access_token.strip().split('.')
        if len(token_parts) != 3:
            logger.warning("Token de acesso com formato inválido")
            raise AuthenticationException("Formato de token inválido")
    
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
            
            # Converter string para UserId
            user_id = UserId(value=user_id_str)
            
            # Buscar usuário no repositório
            user = await self._user_repository.find_by_id(user_id)
            
            if not user:
                logger.warning(f"Usuário não encontrado para ID: {user_id_str}")
                raise UserNotFoundException("Usuário não encontrado")
            
            logger.debug(f"Usuário encontrado: {user.username.value}")
            return user
            
        except UserNotFoundException:
            raise
        except ValueError as e:
            # Erro de validação do UserId (UUID inválido)
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
        
        # Verificar se o usuário está ativo (se houver campo is_active)
        if hasattr(user, 'is_active') and not user.is_active:
            logger.warning(f"Tentativa de acesso com usuário inativo: {user.username.value}")
            raise AuthenticationException("Usuário inativo")
        
        logger.debug(f"Status do usuário {user.username.value} verificado com sucesso")
    
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
