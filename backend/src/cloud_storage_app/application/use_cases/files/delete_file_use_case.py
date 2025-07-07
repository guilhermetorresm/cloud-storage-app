"""
Caso de uso para deletar um arquivo específico do usuário autenticado.
Responsável por validar token JWT, remover arquivo do S3 e deletar metadados do banco.
"""

import logging
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
from cloud_storage_app.infrastructure.database.repositories import (
    AudioFileRepository, ImageFileRepository, VideoFileRepository
)
from cloud_storage_app.domain.value_objects.user_id import UserId
from cloud_storage_app.domain.value_objects.file_id import FileId
from cloud_storage_app.domain.services.storage_service import IStorageService
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService, TokenPayload
from cloud_storage_app.application.dtos.file_dtos import DeleteFileInputDTO

# Exceções da camada de aplicação
from cloud_storage_app.application.exceptions import (
    AuthenticationException,
    ValidationException,
    UserNotFoundException as AppUserNotFoundException,
    AuthorizationException
)

# Exceções do domínio
from cloud_storage_app.domain.exceptions import (
    FileNotFoundException,
    FileValidationException,
    FileAccessDeniedException,
    UserNotFoundException as DomainUserNotFoundException
)

# Exceções da infraestrutura de autenticação
from cloud_storage_app.infrastructure.auth import (
    InvalidTokenException,
    ExpiredTokenException,
    JWTException
)

logger = logging.getLogger(__name__)


class DeleteFileUseCase:
    """
    Caso de uso para deletar um arquivo específico do usuário autenticado.
    
    Responsabilidades:
    - Decodificar e validar token JWT
    - Validar ID do arquivo
    - Buscar arquivo por ID
    - Verificar se o usuário é proprietário do arquivo
    - Remover arquivo do S3
    - Deletar metadados do banco de dados
    - Tratar erros de token inválido, arquivo não encontrado ou sem permissão
    """
    
    @inject
    def __init__(
        self,
        jwt_service: JWTService,
        storage_service: IStorageService = Provide["storage_service"],
    ):
        self._jwt_service = jwt_service
        self._storage_service = storage_service
        self._db_session = None  # Será definida no execute()
        self._user_repository = None  # Será criada no execute()
        self._audio_repository = None  # Será criada no execute()
        self._image_repository = None  # Será criada no execute()
        self._video_repository = None  # Será criada no execute()
        logger.debug("DeleteFileUseCase inicializado")
    
    async def execute(
        self, 
        request: DeleteFileInputDTO, 
        access_token: str, 
        db_session: AsyncSession
    ) -> None:
        """
        Executa o caso de uso para deletar um arquivo específico.
        
        Args:
            request: DeleteFileInputDTO contendo ID do arquivo
            access_token: Token JWT de acesso
            db_session: Sessão do banco de dados
            
        Raises:
            AuthenticationException: Se o token for inválido, expirado ou usuário não encontrado
            ValidationException: Se o ID do arquivo for inválido
            FileNotFoundException: Se o arquivo não for encontrado
            FileAccessDeniedException: Se o usuário não tiver permissão para deletar o arquivo
            FileValidationException: Se houver erro na busca de arquivo
        """
        self._db_session = db_session
        self._user_repository = UserRepository(session=db_session)
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)

        try:
            logger.debug(f"Iniciando processo de deleção do arquivo: {request.file_id}")
            
            # 1. Validar entrada
            self._validate_request(request, access_token)
            
            # 2. Decodificar e validar token JWT
            token_payload = await self._decode_and_validate_token(access_token)
            
            # 3. Buscar usuário no repositório
            user = await self._find_user_by_id(token_payload.sub)
            
            # 4. Verificar status do usuário
            self._check_user_status(user)
            
            # 5. Buscar arquivo por ID
            file_entity = await self._find_file_by_id(request.file_id)
            
            # 6. Verificar se o usuário é proprietário do arquivo
            self._check_file_ownership(file_entity, user.user_id)
            
            # 7. Remover arquivo do S3
            await self._delete_file_from_storage(file_entity)
            
            # 8. Deletar metadados do banco de dados
            await self._delete_file_metadata(file_entity)
            
            # 9. Commit da transação
            await db_session.commit()
            
            logger.info(f"Arquivo {request.file_id} deletado com sucesso pelo usuário: {user.username.value}")
            
        except (AuthenticationException, AppUserNotFoundException, ValidationException, 
                FileNotFoundException, FileValidationException, FileAccessDeniedException):
            # Rollback em caso de erro
            await db_session.rollback()
            raise
        except Exception as e:
            # Rollback em caso de erro inesperado
            await db_session.rollback()
            logger.error(f"Erro inesperado ao deletar arquivo: {str(e)}")
            logger.debug(f"Detalhes do erro: {e.__class__.__name__}: {str(e)}")
            raise FileValidationException("Erro interno ao deletar arquivo") from e
    
    def _validate_request(self, request: DeleteFileInputDTO, access_token: str) -> None:
        """
        Valida os dados de entrada do request.
        
        Args:
            request: Request com ID do arquivo
            access_token: Token JWT de acesso
            
        Raises:
            AuthenticationException: Se o token estiver inválido
            ValidationException: Se o ID do arquivo for inválido
        """
        if not access_token or not access_token.strip():
            logger.warning("Token de acesso não fornecido")
            raise AuthenticationException("Token de acesso é obrigatório")
        
        # Verificar formato básico do token
        token_parts = access_token.strip().split('.')
        if len(token_parts) != 3:
            logger.warning("Token de acesso com formato inválido")
            raise AuthenticationException("Formato de token inválido")
        
        # Validar ID do arquivo
        if not request.file_id:
            logger.warning("ID do arquivo não fornecido")
            raise ValidationException("ID do arquivo é obrigatório")
        
        # Validar formato do UUID
        try:
            UUID(str(request.file_id))
        except (ValueError, TypeError) as e:
            logger.warning(f"ID do arquivo com formato inválido: {request.file_id}")
            raise ValidationException("Formato de ID do arquivo inválido") from e
        
        logger.debug("Parâmetros de request validados com sucesso")
    
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
            AppUserNotFoundException: Se o usuário não for encontrado
            AuthenticationException: Para outros erros de busca
        """
        try:
            logger.debug(f"Buscando usuário por ID: {user_id_str}")
            
            user_id = UserId.from_string(user_id_str)
            user = await self._user_repository.find_by_id(user_id)
            
            if not user:
                logger.warning(f"Usuário não encontrado para ID: {user_id_str}")
                raise AppUserNotFoundException("Usuário não encontrado")
            
            logger.debug(f"Usuário encontrado: {user.username.value}")
            return user
            
        except AppUserNotFoundException:
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
            logger.warning(f"Tentativa de acesso com usuário inativo: {user.username.value}")
            raise AuthenticationException("Usuário inativo")
        
        logger.debug(f"Status do usuário {user.username.value} verificado com sucesso")
    
    async def _find_file_by_id(self, file_id: UUID):
        """
        Busca arquivo por ID em todos os repositórios.

        Args:
            file_id: UUID do arquivo

        Returns:
            Entidade do arquivo encontrado

        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            ValidationException: Se o ID for inválido
            FileValidationException: Se houver erro inesperado
        """
        logger.debug(f"Buscando arquivo por ID: {file_id}")

        try:
            file_id_vo = FileId.from_string(str(file_id))

            repositories = [
                ("áudio", self._audio_repository),
                ("imagem", self._image_repository),
                ("vídeo", self._video_repository)
            ]

            for nome, repo in repositories:
                try:
                    file_entity = await repo.find_by_id(file_id_vo)
                    if file_entity:
                        logger.debug(f"Arquivo de {nome} encontrado: {file_id}")
                        return file_entity
                except Exception as e:
                    logger.debug(f"Erro ao buscar no repositório de {nome}: {e}")

            logger.warning(f"Arquivo não encontrado em nenhum repositório: {file_id}")
            raise FileNotFoundException(str(file_id))

        except FileNotFoundException:
            raise
        except ValueError as e:
            logger.error(f"ID de arquivo inválido: {e}")
            raise ValidationException("ID de arquivo inválido") from e
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar arquivo por ID: {e}")
            raise FileValidationException("Erro ao buscar arquivo") from e
    
    def _check_file_ownership(self, file_entity, user_id: UserId) -> None:
        """
        Verifica se o usuário é proprietário do arquivo.
        
        Args:
            file_entity: Entidade do arquivo
            user_id: ID do usuário
            
        Raises:
            FileAccessDeniedException: Se o usuário não for proprietário
            FileNotFoundException: Se o arquivo estiver marcado como excluído
        """
        if not file_entity:
            raise FileValidationException("Arquivo inválido")
        
        if file_entity.owner_id != user_id:
            logger.warning(f"Tentativa de deleção de arquivo sem permissão. Usuário: {user_id}, Arquivo: {file_entity.file_id}")
            raise FileAccessDeniedException(str(file_entity.file_id), str(user_id))
        
        # Verificar se o arquivo não está já excluído
        if hasattr(file_entity, 'is_deleted') and file_entity.is_deleted:
            logger.warning(f"Tentativa de deleção de arquivo já excluído: {file_entity.file_id}")
            raise FileNotFoundException(str(file_entity.file_id))
        
        logger.debug(f"Verificação de propriedade bem-sucedida para arquivo: {file_entity.file_id}")
    
    async def _delete_file_from_storage(self, file_entity) -> None:
        """
        Remove o arquivo do serviço de armazenamento S3.
        
        Args:
            file_entity: Entidade do arquivo
            
        Raises:
            FileValidationException: Se houver erro na remoção do arquivo
        """
        try:
            logger.debug(f"Removendo arquivo do S3: {file_entity.file_id}")
            
            # Verificar se a entidade tem o atributo path
            if not hasattr(file_entity, 'path') or not file_entity.path:
                logger.warning(f"Arquivo sem caminho definido: {file_entity.file_id}")
                raise FileValidationException("Caminho do arquivo não definido")
            
            # Verificar se o arquivo existe no S3 antes de tentar deletar
            file_exists = await self._storage_service.file_exists(file_entity.path)
            if not file_exists:
                logger.warning(f"Arquivo não encontrado no S3: {file_entity.path}")
                # Continuar com a deleção dos metadados mesmo se o arquivo não existir no S3
                return
            
            # Deletar arquivo do S3
            await self._storage_service.delete_file(file_entity.path)
            
            logger.debug(f"Arquivo removido do S3 com sucesso: {file_entity.file_id}")
            
        except Exception as e:
            logger.error(f"Erro ao remover arquivo do S3: {str(e)}")
            raise FileValidationException("Erro ao remover arquivo do armazenamento") from e
    
    async def _delete_file_metadata(self, file_entity) -> None:
        """
        Deleta os metadados do arquivo do banco de dados.
        
        Args:
            file_entity: Entidade do arquivo
            
        Raises:
            FileValidationException: Se houver erro na deleção dos metadados
        """
        try:
            logger.debug(f"Deletando metadados do arquivo: {file_entity.file_id}")
            
            # Obter o repositório apropriado para a entidade
            repository = self._get_repository_for_entity(file_entity)
            
            # Deletar do banco de dados
            await repository.delete(file_entity.file_id)
            
            logger.debug(f"Metadados do arquivo deletados com sucesso: {file_entity.file_id}")
            
        except Exception as e:
            logger.error(f"Erro ao deletar metadados do arquivo: {str(e)}")
            raise FileValidationException("Erro ao deletar metadados do arquivo") from e
    
    def _get_repository_for_entity(self, file_entity):
        """
        Retorna o repositório apropriado para a entidade.
        
        Args:
            file_entity: Entidade do arquivo
            
        Returns:
            Repositório apropriado
            
        Raises:
            FileValidationException: Se o tipo de arquivo não for suportado
        """
        if hasattr(file_entity, 'is_audio') and file_entity.is_audio:
            return self._audio_repository
        elif hasattr(file_entity, 'is_image') and file_entity.is_image:
            return self._image_repository
        elif hasattr(file_entity, 'is_video') and file_entity.is_video:
            return self._video_repository
        else:
            # Fallback: detectar pelo tipo da entidade
            entity_type = file_entity.__class__.__name__
            if 'Audio' in entity_type:
                return self._audio_repository
            elif 'Image' in entity_type:
                return self._image_repository
            elif 'Video' in entity_type:
                return self._video_repository
            else:
                logger.error(f"Tipo de entidade não suportado: {entity_type}")
                raise FileValidationException("Tipo de arquivo não suportado")