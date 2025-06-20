"""
Caso de uso para alteração de senha do usuário.
Responsável por validar senha atual, verificar se a nova senha é diferente
e atualizar a senha do usuário no banco de dados.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.domain.value_objects import Password, HashedPassword
from cloud_storage_app.domain.value_objects.user_id import UserId
from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
from cloud_storage_app.application.dtos.user_dtos import ChangePasswordDTO
from cloud_storage_app.infrastructure.auth.password_service import PasswordService
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService
from cloud_storage_app.infrastructure.auth import (
    JWTException,
    InvalidTokenException,
    ExpiredTokenException
)
from cloud_storage_app.domain.exceptions.user_exceptions import (
    UserNotFoundException,
    UserValidationException,
    InvalidPasswordException
)
from cloud_storage_app.application.exceptions import (
    AuthenticationException
)

logger = logging.getLogger(__name__)


class ChangePasswordUseCase:
    """
    Caso de uso para alteração de senha do usuário.
    
    Responsabilidades:
    - Decodificar token JWT para obter user_id
    - Validar se a senha atual está correta
    - Verificar se a nova senha é diferente da atual
    - Hashear a nova senha
    - Atualizar a senha no banco de dados
    - Tratar erros de validação e autenticação
    """
    
    def __init__(
        self,
        password_service: PasswordService,
        jwt_service: JWTService,
    ):
        self._password_service = password_service
        self._jwt_service = jwt_service
        self._db_session = None
        self._user_repository = None
        logger.debug("ChangePasswordUseCase inicializado")
    
    async def execute(
        self, 
        access_token: str,
        change_password_dto: ChangePasswordDTO, 
        db_session: AsyncSession
    ) -> None:
        """
        Executa o caso de uso para alterar a senha do usuário.
        
        Args:
            access_token: Token JWT do usuário autenticado
            change_password_dto: DTO com senha atual e nova senha
            db_session: Sessão do banco de dados
            
        Raises:
            UserNotFoundException: Se o usuário não for encontrado
            AuthenticationException: Se a senha atual estiver incorreta ou token inválido
            InvalidPasswordException: Se a nova senha não atender aos requisitos
            UserValidationException: Se houver erro de validação
        """
        # Criar repositório com a sessão
        self._db_session = db_session
        self._user_repository = UserRepository(session=db_session)
        
        logger.debug("Iniciando alteração de senha para usuário autenticado")
        
        try:
            # 1. Validar dados de entrada
            self._validate_input(change_password_dto)
            
            # 2. Decodificar token e obter user_id
            user_id = await self._extract_user_id_from_token(access_token)
            
            # 3. Buscar usuário no banco de dados
            user = await self._find_user_by_id(user_id)
            
            # 4. Verificar senha atual
            await self._verify_current_password(user, change_password_dto.current_password)
            
            # 5. Verificar se a nova senha é diferente da atual
            self._check_password_difference(change_password_dto)
            
            # 6. Hashear nova senha
            new_hashed_password = self._hash_new_password(change_password_dto.new_password)
            
            # 7. Atualizar senha na entidade
            user.change_password(new_hashed_password)
            
            # 8. Persistir mudanças no banco de dados usando o repositório
            await self._user_repository.save(user)
            
            # 9. Confirmar transação
            await self._db_session.commit()
            
            logger.info(f"Senha alterada com sucesso para usuário: {user.username.value}")
            
        except (
            UserNotFoundException,
            AuthenticationException,
            InvalidPasswordException,
            UserValidationException
        ) as e:
            logger.error(f"Erro ao alterar senha: {str(e)}")
            await self._db_session.rollback()
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao alterar senha: {str(e)}")
            await self._db_session.rollback()
            raise

    async def _extract_user_id_from_token(self, access_token: str) -> str:
        """
        Extrai o user_id do token JWT com validação completa.
        
        Args:
            access_token: Token JWT de acesso
            
        Returns:
            str: ID do usuário extraído do token
            
        Raises:
            AuthenticationException: Se o token for inválido, expirado ou não for um access token
        """
        try:
            logger.debug("Iniciando extração de user_id do token JWT")
            
            # Validar entrada
            if not access_token or not access_token.strip():
                logger.warning("Token vazio fornecido")
                raise AuthenticationException("Token de acesso é obrigatório")
            
            # Decodificar token e obter payload
            payload = self._jwt_service.decode_token(access_token)
            
            # Validar se é access token (não refresh token)
            if not self._jwt_service.validate_token_type(payload, "access"):
                logger.warning("Token fornecido não é um access token")
                raise AuthenticationException("Operação requer token de acesso válido")
            
            # Extrair user_id do payload
            user_id = payload.sub
            if not user_id:
                logger.error("Token válido mas sem subject (user_id)")
                raise AuthenticationException("Token inválido: identificador de usuário não encontrado")
            
            logger.debug(f"User ID extraído com sucesso: {user_id}")
            return user_id
            
        except AuthenticationException:
            # Re-lançar exceções de autenticação já processadas
            raise
            
        except ExpiredTokenException as e:
            logger.warning(f"Token expirado durante extração de user_id: {str(e)}")
            raise AuthenticationException("Token expirado. Faça login novamente") from e
            
        except InvalidTokenException as e:
            logger.warning(f"Token inválido durante extração de user_id: {str(e)}")
            raise AuthenticationException("Token inválido. Faça login novamente") from e
            
        except JWTException as e:
            logger.error(f"Erro do serviço JWT: {str(e)}")
            raise AuthenticationException("Erro ao processar token de autenticação") from e
            
        except Exception as e:
            logger.error(f"Erro inesperado ao extrair user_id: {str(e)}", exc_info=True)
            raise AuthenticationException("Erro interno ao processar autenticação") from e
    
    def _validate_input(self, change_password_dto: ChangePasswordDTO) -> None:
        """
        Valida os dados de entrada do DTO.
        
        Args:
            change_password_dto: DTO com os dados de alteração de senha
            
        Raises:
            UserValidationException: Se os dados estiverem inválidos
        """
        if not change_password_dto.current_password:
            raise UserValidationException("Senha atual é obrigatória")
        
        if not change_password_dto.new_password:
            raise UserValidationException("Nova senha é obrigatória")
        
        if len(change_password_dto.current_password.strip()) < 8:
            raise UserValidationException("Senha atual deve ter pelo menos 8 caracteres")
        
        if len(change_password_dto.new_password.strip()) < 8:
            raise UserValidationException("Nova senha deve ter pelo menos 8 caracteres")
    
    async def _find_user_by_id(self, user_id_str: str) -> User:
        """
        Busca usuário pelo ID.
        
        Args:
            user_id_str: String do ID do usuário
            
        Returns:
            User: Entidade do usuário encontrado
            
        Raises:
            UserNotFoundException: Se o usuário não for encontrado
            UserValidationException: Se o ID for inválido
        """
        try:
            logger.debug(f"Buscando usuário por ID: {user_id_str}")
            
            # Converter string para UserId
            user_id = UserId.from_string(user_id_str)
            
            # Buscar usuário no repositório
            user = await self._user_repository.find_by_id(user_id)
            
            if not user:
                logger.warning(f"Usuário não encontrado para ID: {user_id_str}")
                raise UserNotFoundException("Usuário não encontrado")
            
            # Verificar se o usuário está ativo
            if hasattr(user, 'is_active') and not user.is_active:
                logger.warning(f"Tentativa de alterar senha de usuário inativo: {user.username.value}")
                raise AuthenticationException("Usuário inativo")
            
            logger.debug(f"Usuário encontrado: {user.username.value}")
            return user
            
        except UserNotFoundException:
            raise
        except AuthenticationException:
            raise
        except ValueError as e:
            logger.error(f"ID de usuário inválido: {str(e)}")
            raise UserValidationException("ID de usuário inválido") from e
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {str(e)}")
            raise UserValidationException("Erro ao buscar usuário") from e
    
    async def _verify_current_password(self, user: User, current_password: str) -> None:
        """
        Verifica se a senha atual fornecida está correta.
        
        Args:
            user: Entidade do usuário
            current_password: Senha atual fornecida pelo usuário
            
        Raises:
            AuthenticationException: Se a senha atual estiver incorreta
        """
        try:
            logger.debug(f"Verificando senha atual para usuário: {user.username.value}")
            
            # Criar value object Password para validação
            password_vo = Password(current_password)
            
            # Verificar se a senha atual está correta
            is_valid = self._password_service.verify_password(
                password_vo,
                user.hashed_password
            )
            
            if not is_valid:
                logger.warning(f"Senha atual incorreta para usuário: {user.username.value}")
                raise AuthenticationException("Senha atual incorreta")
            
            logger.debug("Senha atual verificada com sucesso")
            
        except ValueError as e:
            logger.error(f"Erro de validação na senha atual: {str(e)}")
            raise InvalidPasswordException(f"Senha atual inválida: {str(e)}") from e
        except AuthenticationException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar senha atual: {str(e)}")
            raise AuthenticationException("Erro ao verificar senha atual") from e
    
    def _check_password_difference(self, change_password_dto: ChangePasswordDTO) -> None:
        """
        Verifica se a nova senha é diferente da senha atual.
        
        Args:
            change_password_dto: DTO com as senhas
            
        Raises:
            UserValidationException: Se as senhas forem iguais
        """
        if change_password_dto.current_password == change_password_dto.new_password:
            logger.warning("Tentativa de alterar senha para a mesma senha atual")
            raise UserValidationException("A nova senha deve ser diferente da senha atual")
        
        logger.debug("Nova senha é diferente da atual - validação passou")
    
    def _hash_new_password(self, new_password: str) -> HashedPassword:
        """
        Cria hash da nova senha.
        
        Args:
            new_password: Nova senha em texto plano
            
        Returns:
            HashedPassword: Value object com a senha hasheada
            
        Raises:
            InvalidPasswordException: Se houver erro ao hashear a senha
        """
        try:
            logger.debug("Criando hash da nova senha")
            
            # Criar value object Password
            password_vo = Password(new_password)
            
            # Hashear a nova senha
            hashed_password = self._password_service.hash_password(password_vo)
            
            logger.debug("Nova senha hasheada com sucesso")
            return hashed_password
            
        except ValueError as e:
            logger.error(f"Erro de validação na nova senha: {str(e)}")
            raise InvalidPasswordException(f"Nova senha inválida: {str(e)}") from e
        except Exception as e:
            logger.error(f"Erro inesperado ao hashear nova senha: {str(e)}")
            raise InvalidPasswordException("Erro ao processar nova senha") from e