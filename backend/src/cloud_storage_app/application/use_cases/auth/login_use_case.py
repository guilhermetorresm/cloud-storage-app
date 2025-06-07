"""
Caso de uso para autenticação de usuários (Login).
Responsável por validar credenciais e gerar tokens JWT.
"""

import logging
from typing import Optional
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject

from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.domain.repositories.user_repository import UserRepository
from cloud_storage_app.infrastructure.auth.password_service import PasswordService
from cloud_storage_app.domain.value_objects import Username, Password
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService, JWTTokens
from cloud_storage_app.application.dtos.user_dtos import UserLoginDTO, UserLoginResponseDTO, UserResponseSimpleDTO
from cloud_storage_app.application.exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
    UserNotFoundException
)

logger = logging.getLogger(__name__)


class LoginUseCase:
    """
    Caso de uso para autenticação de usuários.
    
    Responsabilidades:
    - Validar credenciais do usuário
    - Verificar se o usuário existe
    - Comparar senha fornecida com hash armazenado
    - Gerar tokens JWT em caso de sucesso
    """
    
    @inject
    def __init__(
        self,
        user_repository: UserRepository = Provide["user_repository"],
        password_service: PasswordService = Provide["password_service"],
        jwt_service: JWTService = Provide["jwt_service"],
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._jwt_service = jwt_service
        logger.debug("LoginUseCase inicializado")
    
    async def execute(self, request: UserLoginDTO) -> UserLoginResponseDTO:
        """
        Executa o caso de uso de login.
        
        Args:
            request: UserLoginDTO, Dados de login (username e password)
            
        Returns:
            UserLoginResponseDTO: Dados de resposta incluindo tokens JWT
            
        Raises:
            InvalidCredentialsException: Se as credenciais estiverem incorretas
            UserNotFoundException: Se o usuário não for encontrado
            AuthenticationException: Para outros erros de autenticação
        """
        try:
            logger.info(f"Tentativa de login para usuário: {request.username}")
            
            # 1. Validar entrada
            await self._validate_request(request)
            
            # 2. Buscar usuário por username
            user = await self._find_user_by_username(request.username)
            if not user:
                logger.error("Usuário não encontrado após busca")
                raise UserNotFoundException("Usuário não encontrado")
            
            logger.debug(f"Usuário encontrado: {user.__dict__}")
            
            # 3. Verificar se o usuário está ativo
            self._check_user_status(user)
            
            # 4. Validar senha
            await self._validate_password(request.password, user)
            
            # 5. Gerar tokens JWT
            tokens = self._generate_tokens(user)
            
            # 6. Registrar login bem-sucedido
            await self._log_successful_login(user)

            user_response = UserResponseSimpleDTO(
                user_id=str(user.user_id.value),
                username=user.username.value,
                email=user.email.value,
                first_name=user.first_name.value,
                last_name=user.last_name.value if user.last_name else None,
            )
            
            # 7. Preparar resposta
            response = UserLoginResponseDTO(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type=tokens.token_type,
                user=user_response
            )
            
            logger.info(f"Login realizado com sucesso para usuário: {user.username.value}")
            return response
            
        except (InvalidCredentialsException, UserNotFoundException, AuthenticationException):
            # Re-raise exceções conhecidas
            raise
        except Exception as e:
            logger.error(f"Erro inesperado durante login: {str(e)}")
            logger.debug(f"Detalhes do erro: {e.__class__.__name__}: {str(e)}")
            raise AuthenticationException("Erro interno durante autenticação") from e
    
    async def _validate_request(self, request: UserLoginDTO) -> None:
        """
        Valida os dados de entrada do request.
        
        Args:
            request: Request de login
            
        Raises:
            InvalidCredentialsException: Se os dados estiverem inválidos
        """
        if not request.username or not request.username.strip():
            raise InvalidCredentialsException("Username é obrigatório")
        
        if not request.password:
            raise InvalidCredentialsException("Senha é obrigatória")
        
        # Validar formato do username usando value object
        try:
            Username(value=request.username.strip())
        except ValueError as e:
            raise InvalidCredentialsException("Username ou Senha inválidos") from e
        
        # Validar formato da senha usando value object
        try:
            Password(value=request.password)
        except ValueError as e:
            raise InvalidCredentialsException("Username ou Senha inválidos") from e
    

    async def _find_user_by_username(self, username_str: str) -> User:
        """
        Busca usuário pelo username.
        
        Args:
            username_str: String do username
            
        Returns:
            User: Entidade do usuário encontrado
            
        Raises:
            UserNotFoundException: Se o usuário não for encontrado
        """
        try:
            username = Username(value=username_str.strip())
            user = await self._user_repository.find_by_username(username)
            
            if not user:
                logger.warning(f"Tentativa de login com username inexistente: {username_str}")
                raise UserNotFoundException("Usuário não encontrado")
            
            return user
            
        except UserNotFoundException:
            raise
        except ValueError as e:
            # Tratamento específico para erro de UUID
            logger.error(f"Erro de validação de UUID: {str(e)}")
            raise UserNotFoundException("Usuário não encontrado") from e
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por username: {str(e)}")
            raise AuthenticationException("Erro ao buscar usuário") from e


    def _check_user_status(self, user: User) -> None:
        """
        Verifica se o usuário está em status válido para login.
        
        Args:
            user: Entidade do usuário
            
        Raises:
            AuthenticationException: Se o usuário não puder fazer login
        """
        # Verificar se o usuário está ativo (caso tenha campo is_active)
        # Por enquanto, assumimos que todos os usuários podem fazer login
        # Esta validação pode ser expandida no futuro
        
        if not user:
            raise AuthenticationException("Status de usuário inválido")
        
        logger.debug(f"Status do usuário {user.username.value} verificado com sucesso")
    
    async def _validate_password(self, password_str: str, user: User) -> None:
        """
        Valida a senha fornecida contra o hash armazenado.
        
        Args:
            password_str: Senha em texto plano
            user: Entidade do usuário
            
        Raises:
            InvalidCredentialsException: Se a senha estiver incorreta
        """
        try:
            password = Password(value=password_str)
            
            # Verificar senha usando o serviço de password
            is_valid = self._password_service.verify_password(password, user.hashed_password)
            
            if not is_valid:
                logger.warning(f"Tentativa de login com senha incorreta para usuário: {user.username.value}")
                raise InvalidCredentialsException("Username ou Senha inválidos")
            
            logger.debug(f"Senha validada com sucesso para usuário: {user.username.value}")
            
            # Verificar se a senha precisa ser rehashed (segurança)
            if self._password_service.needs_rehash(user.hashed_password):
                logger.info(f"Senha do usuário {user.username.value} precisa ser atualizada")
                # TODO: Implementar atualização de hash da senha em background
            
        except InvalidCredentialsException:
            raise
        except Exception as e:
            logger.error(f"Erro ao validar senha: {str(e)}")
            raise AuthenticationException("Erro na validação de credenciais") from e
    
    def _generate_tokens(self, user: User) -> JWTTokens:
        """
        Gera tokens JWT para o usuário autenticado.
        
        Args:
            user: Entidade do usuário
            
        Returns:
            JWTTokens: Par de tokens (access + refresh)
            
        Raises:
            AuthenticationException: Se houver erro na geração dos tokens
        """
        try:
            # Preparar claims adicionais (opcional)
            extra_claims = {
                "login_timestamp": int(user.created_at.timestamp()) if user.created_at else None,
                # Adicionar outros claims conforme necessário
            }
            
            # Gerar par de tokens
            tokens = self._jwt_service.create_token_pair(
                user_id=user.user_id,
                email=user.email.value,
                username=user.username.value,
                extra_claims=extra_claims
            )
            
            logger.debug(f"Tokens JWT gerados para usuário: {user.username.value}")
            return tokens
            
        except Exception as e:
            logger.error(f"Erro ao gerar tokens JWT: {str(e)}")
            raise AuthenticationException("Erro na geração de tokens") from e
    
    async def _log_successful_login(self, user: User) -> None:
        """
        Registra informações sobre login bem-sucedido.
        
        Args:
            user: Entidade do usuário
        """
        try:
            # Registrar evento de login (audit log)
            logger.info(f"Login bem-sucedido - Usuário: {user.username.value}, ID: {user.user_id.value}")
            
            # TODO: Implementar auditoria de login se necessário
            # - Registrar IP do usuário
            # - Registrar timestamp
            # - Registrar user agent
            # - Atualizar last_login no usuário
            
        except Exception as e:
            # Não deve falhar o login se o log falhar
            logger.warning(f"Erro ao registrar login bem-sucedido: {str(e)}")
            logger.debug(f"Detalhes do usuário: {user.__dict__}")
