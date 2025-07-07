"""
Caso de uso para obter detalhes de um arquivo específico do usuário autenticado.
Responsável por validar token JWT, buscar arquivo por ID e gerar URL de download.
"""

import logging
from typing import Optional
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
from cloud_storage_app.application.dtos.file_dtos import (
    GetFileDetailsInputDTO, FileDetailsOutputDTO,
    entity_to_specific_dto
)
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
from cloud_storage_app.domain.exceptions import (
    FileNotFoundException,
    FileValidationException,
    FileAccessDeniedException
)

logger = logging.getLogger(__name__)


class GetFileDetailsUseCase:
    """
    Caso de uso para obter detalhes de um arquivo específico do usuário autenticado.
    
    Responsabilidades:
    - Decodificar e validar token JWT
    - Validar ID do arquivo
    - Buscar arquivo por ID
    - Verificar se o usuário é proprietário do arquivo
    - Gerar URL de download temporária
    - Retornar detalhes completos do arquivo
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
        logger.debug("GetFileDetailsUseCase inicializado")
    
    async def execute(
        self, 
        request: GetFileDetailsInputDTO, 
        access_token: str, 
        db_session: AsyncSession
    ) -> FileDetailsOutputDTO:
        """
        Executa o caso de uso para obter detalhes de um arquivo específico.
        
        Args:
            request: GetFileDetailsInputDTO contendo ID do arquivo
            access_token: Token JWT de acesso
            db_session: Sessão do banco de dados
            
        Returns:
            FileDetailsOutputDTO: Detalhes completos do arquivo com URL de download
            
        Raises:
            AuthenticationException: Se o token for inválido, expirado ou usuário não encontrado
            ValidationException: Se o ID do arquivo for inválido
            FileNotFoundException: Se o arquivo não for encontrado
            FileValidationException: Se houver erro na busca de arquivo ou falta de permissão
        """
        self._db_session = db_session
        self._user_repository = UserRepository(session=db_session)
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)

        try:
            logger.debug(f"Iniciando processo de busca de detalhes do arquivo: {request.file_id}")
            
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
            
            # 7. Gerar URL de download
            download_url = await self._generate_download_url(file_entity)
            
            # 8. Converter para DTO específico
            file_dto = entity_to_specific_dto(file_entity)
            
            # 9. Atualizar última data de acesso (opcional)
            await self._update_last_accessed(file_entity)
            
            logger.info(f"Detalhes do arquivo {request.file_id} obtidos com sucesso para usuário: {user.username.value}")
            
            return FileDetailsOutputDTO(
                metadata=file_dto,
                download_url=download_url
            )
            
        except (AuthenticationException, UserNotFoundException, ValidationException, 
                FileNotFoundException, FileValidationException, FileAccessDeniedException):
            # Re-raise exceções conhecidas
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao obter detalhes do arquivo: {str(e)}")
            logger.debug(f"Detalhes do erro: {e.__class__.__name__}: {str(e)}")
            raise FileValidationException("Erro interno ao obter detalhes do arquivo") from e
    
    def _validate_request(self, request: GetFileDetailsInputDTO, access_token: str) -> None:
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
            UserNotFoundException: Se o usuário não for encontrado
            AuthenticationException: Para outros erros de busca
        """
        try:
            logger.debug(f"Buscando usuário por ID: {user_id_str}")
            
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
            FileValidationException: Se houver erro na busca
        """
        logger.debug(f"Buscando arquivo por ID: {file_id}")
        
        try:
            file_id_vo = FileId.from_string(str(file_id))
            
            repositories = [
                self._audio_repository,
                self._image_repository,
                self._video_repository
            ]
            
            for repository in repositories:
                try:
                    file_entity = await repository.find_by_id(file_id_vo)
                    if file_entity:
                        logger.debug(f"Arquivo encontrado em: {repository.__class__.__name__}")
                        return file_entity
                except Exception as e:
                    logger.debug(f"Falha ao buscar em {repository.__class__.__name__}: {e}")
            
            logger.warning(f"Arquivo não encontrado em nenhum repositório: {file_id}")
            raise FileNotFoundException(str(file_id))

        except FileNotFoundException:
            raise
        except ValueError as e:
            logger.error(f"UUID inválido: {e}")
            raise ValidationException("ID de arquivo inválido") from e
        except Exception as e:
            logger.error(f"Erro inesperado na busca do arquivo: {e}")
            raise FileValidationException("Erro ao buscar arquivo") from e
    
    def _check_file_ownership(self, file_entity, user_id: UserId) -> None:
        """
        Verifica se o usuário é proprietário do arquivo.
        
        Args:
            file_entity: Entidade do arquivo
            user_id: ID do usuário
            
        Raises:
            FileValidationException: Se o usuário não for proprietário
        """
        if not file_entity:
            raise FileValidationException("Arquivo inválido")
        
        if file_entity.owner_id != user_id:
            logger.warning(f"Tentativa de acesso a arquivo sem permissão...")
            raise FileAccessDeniedException(
                file_id=str(file_entity.file_id.value),
                user_id=str(user_id.value)
            )
        
        # Verificar se o arquivo não está excluído
        if hasattr(file_entity, 'is_deleted') and file_entity.is_deleted:
            logger.warning(f"Tentativa de acesso a arquivo excluído: {file_entity.file_id}")
            raise FileNotFoundException(str(file_entity.file_id.value))
        
        logger.debug(f"Verificação de propriedade bem-sucedida para arquivo: {file_entity.file_id}")
    
    async def _generate_download_url(self, file_entity) -> Optional[str]:
        """
        Gera URL de download temporária para o arquivo usando o S3StorageService.
        
        Args:
            file_entity: Entidade do arquivo
            
        Returns:
            Optional[str]: URL de download ou None se não disponível
        """
        try:
            logger.debug(f"Gerando URL de download para arquivo: {file_entity.file_id}")
            
            # Verificar se a entidade tem o atributo path
            if not hasattr(file_entity, 'path') or not file_entity.path:
                logger.warning(f"Arquivo sem caminho definido: {file_entity.file_id}")
                return None
            
            # Gerar URL pré-assinada usando o S3StorageService
            # Configurar tempo de expiração para 1 hora (3600 segundos)
            expiration_seconds = 3600
            
            download_url = await self._storage_service.get_presigned_url(
                file_path=file_entity.path,
                expiration=expiration_seconds
            )
            
            if download_url:
                logger.debug(f"URL de download gerada com sucesso para arquivo: {file_entity.file_id}")
                return download_url
            else:
                logger.warning(f"Não foi possível gerar URL de download para arquivo: {file_entity.file_id}")
                # Fallback para endpoint interno em caso de falha
                return f"/api/v1/files/{file_entity.file_id.value}/download"
            
        except Exception as e:
            logger.error(f"Erro ao gerar URL de download: {str(e)}")
            # Retornar endpoint interno em caso de erro
            return f"/api/v1/files/{file_entity.file_id.value}/download"
    
    async def _update_last_accessed(self, file_entity) -> None:
        """
        Atualiza a última data de acesso do arquivo.
        
        Args:
            file_entity: Entidade do arquivo
        """
        try:
            logger.debug(f"Atualizando última data de acesso para arquivo: {file_entity.file_id}")
            
            # Atualizar a última data de acesso na entidade
            if hasattr(file_entity, 'update_last_accessed'):
                file_entity.update_last_accessed()
                
                # Salvar no repositório apropriado
                repository = self._get_repository_for_entity(file_entity)
                await repository.update(file_entity)
                
                logger.debug("Última data de acesso atualizada com sucesso")
            else:
                logger.debug("Entidade não suporta atualização de última data de acesso")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar última data de acesso: {str(e)}")
            # Não falhar o caso de uso por erro na atualização
            pass
    
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