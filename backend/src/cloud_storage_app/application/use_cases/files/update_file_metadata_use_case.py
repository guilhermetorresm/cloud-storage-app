"""
Caso de uso para atualização de metadados de arquivo do usuário autenticado.
Responsável por validar token JWT, buscar arquivo por ID e atualizar metadados.
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
from cloud_storage_app.domain.value_objects.file_name import FileName
from cloud_storage_app.domain.value_objects.file_description import FileDescription
from cloud_storage_app.domain.value_objects.tag import Tag
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService, TokenPayload
from cloud_storage_app.application.dtos.file_dtos import (
    UpdateFileMetadataInputDTO, FileResponseDTO, entity_to_specific_dto
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
    FileValidationException
)

logger = logging.getLogger(__name__)


class UpdateFileMetadataUseCase:
    """
    Caso de uso para atualização de metadados de arquivo do usuário autenticado.
    
    Responsabilidades:
    - Decodificar e validar token JWT
    - Validar dados de entrada
    - Buscar arquivo por ID
    - Verificar se o usuário é proprietário do arquivo
    - Atualizar metadados (nome, descrição, tags)
    - Salvar alterações no banco
    - Retornar dados atualizados do arquivo
    - Tratar erros de token inválido, arquivo não encontrado ou sem permissão
    """
    
    @inject
    def __init__(self, jwt_service: JWTService):
        self._jwt_service = jwt_service
        self._db_session = None  # Será definida no execute()
        self._user_repository = None  # Será criada no execute()
        self._audio_repository = None  # Será criada no execute()
        self._image_repository = None  # Será criada no execute()
        self._video_repository = None  # Será criada no execute()
        logger.debug("UpdateFileMetadataUseCase inicializado")
    
    async def execute(
        self, 
        request: UpdateFileMetadataInputDTO, 
        access_token: str, 
        db_session: AsyncSession
    ) -> FileResponseDTO:
        """
        Executa o caso de uso para atualização de metadados de arquivo.
        
        Args:
            request: UpdateFileMetadataInputDTO contendo novos metadados
            access_token: Token JWT de acesso
            db_session: Sessão do banco de dados
            
        Returns:
            FileResponseDTO: Dados atualizados do arquivo
            
        Raises:
            AuthenticationException: Se o token for inválido, expirado ou usuário não encontrado
            ValidationException: Se os dados de entrada forem inválidos
            FileNotFoundException: Se o arquivo não for encontrado
            FileValidationException: Se houver erro na atualização ou falta de permissão
        """
        self._db_session = db_session
        self._user_repository = UserRepository(session=db_session)
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)

        try:
            logger.debug(f"Iniciando atualização de metadados do arquivo: {request.file_id}")
            
            # 1. Validar entrada
            self._validate_request(request, access_token)
            
            # 2. Decodificar e validar token JWT
            token_payload = await self._decode_and_validate_token(access_token)
            
            # 3. Buscar usuário no repositório
            user = await self._find_user_by_id(token_payload.sub)
            
            # 4. Verificar status do usuário
            self._check_user_status(user)
            
            # 5. Buscar arquivo por ID
            file_entity, repository = await self._find_file_by_id(request.file_id, user.user_id)
            
            # 6. Verificar se o arquivo pode ser atualizado
            self._check_file_updateable(file_entity)
            
            # 7. Atualizar metadados
            await self._update_file_metadata(file_entity, request)
            
            # 8. Salvar alterações
            await repository.save(file_entity)
            await self._db_session.commit()
            
            logger.info(f"Metadados do arquivo {request.file_id} atualizados com sucesso para usuário: {user.username.value}")
            
            # 9. Retornar dados atualizados
            return entity_to_specific_dto(file_entity)
            
        except (AuthenticationException, UserNotFoundException, ValidationException, 
                FileNotFoundException, FileValidationException):
            # Re-raise exceções conhecidas
            await self._db_session.rollback()
            raise
        except Exception as e:
            await self._db_session.rollback()
            logger.error(f"Erro inesperado ao atualizar metadados do arquivo: {str(e)}")
            logger.debug(f"Detalhes do erro: {e.__class__.__name__}: {str(e)}")
            raise FileValidationException("Erro interno ao atualizar metadados do arquivo") from e
    
    def _validate_request(self, request: UpdateFileMetadataInputDTO, access_token: str) -> None:
        """
        Valida os dados de entrada do request.
        
        Args:
            request: Request com dados de atualização
            access_token: Token JWT de acesso
            
        Raises:
            AuthenticationException: Se o token estiver inválido
            ValidationException: Se os dados de entrada forem inválidos
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
        
        # Validar se pelo menos um campo foi fornecido para atualização
        if not any([request.new_name, request.new_description, request.new_tags]):
            logger.warning("Nenhum campo fornecido para atualização")
            raise ValidationException("Pelo menos um campo deve ser fornecido para atualização")
        
        # Validar novo nome se fornecido
        if request.new_name is not None:
            try:
                FileName(request.new_name)
            except ValueError as e:
                logger.warning(f"Nome de arquivo inválido: {request.new_name}")
                raise ValidationException(f"Nome de arquivo inválido: {str(e)}") from e
        
        # Validar nova descrição se fornecida
        if request.new_description is not None:
            try:
                FileDescription(request.new_description)
            except ValueError as e:
                logger.warning(f"Descrição de arquivo inválida: {request.new_description}")
                raise ValidationException(f"Descrição de arquivo inválida: {str(e)}") from e
        
        # Validar novas tags se fornecidas
        if request.new_tags is not None:
            for tag in request.new_tags:
                try:
                    Tag(tag)
                except ValueError as e:
                    logger.warning(f"Tag inválida: {tag}")
                    raise ValidationException(f"Tag inválida '{tag}': {str(e)}") from e
        
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
    
    async def _find_file_by_id(self, file_id: UUID, owner_id: UserId):
        """
        Busca arquivo por ID em todos os repositórios e verifica propriedade.
        
        Args:
            file_id: UUID do arquivo
            owner_id: ID do usuário proprietário
            
        Returns:
            Tuple[FileEntity, Repository]: Entidade do arquivo e repositório onde foi encontrado
            
        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            FileValidationException: Se houver erro na busca ou falta de permissão
        """
        logger.debug(f"Buscando arquivo por ID: {file_id}")
        
        try:
            file_id_vo = FileId.from_string(str(file_id))
            
            repositories = [
                (self._audio_repository, "AudioFileRepository"),
                (self._image_repository, "ImageFileRepository"),
                (self._video_repository, "VideoFileRepository")
            ]
            
            for repository, repo_name in repositories:
                try:
                    file_entity = await repository.find_by_id(file_id_vo)
                    if file_entity:
                        logger.debug(f"Arquivo encontrado em: {repo_name}")
                        
                        # Verificar propriedade do arquivo
                        if file_entity.owner_id != owner_id:
                            logger.warning(f"Tentativa de atualização de arquivo sem permissão. Usuário: {owner_id}, Arquivo: {file_id}")
                            raise FileValidationException("Acesso negado ao arquivo")
                        
                        return file_entity, repository
                        
                except FileValidationException:
                    raise
                except Exception as e:
                    logger.debug(f"Falha ao buscar em {repo_name}: {e}")
            
            logger.warning(f"Arquivo não encontrado em nenhum repositório: {file_id}")
            raise FileNotFoundException(str(file_id))

        except (FileNotFoundException, FileValidationException):
            raise
        except ValueError as e:
            logger.error(f"UUID inválido: {e}")
            raise ValidationException("ID de arquivo inválido") from e
        except Exception as e:
            logger.error(f"Erro inesperado na busca do arquivo: {e}")
            raise FileValidationException("Erro ao buscar arquivo") from e
    
    def _check_file_updateable(self, file_entity) -> None:
        """
        Verifica se o arquivo pode ser atualizado.
        
        Args:
            file_entity: Entidade do arquivo
            
        Raises:
            FileValidationException: Se o arquivo não puder ser atualizado
        """
        if not file_entity:
            raise FileValidationException("Arquivo inválido")
        
        # Verificar se o arquivo não está excluído
        if hasattr(file_entity, 'is_deleted') and file_entity.is_deleted:
            logger.warning(f"Tentativa de atualização de arquivo excluído: {file_entity.file_id}")
            raise FileValidationException("Não é possível atualizar um arquivo excluído")
        
        logger.debug(f"Arquivo pode ser atualizado: {file_entity.file_id}")
    
    async def _update_file_metadata(self, file_entity, request: UpdateFileMetadataInputDTO) -> None:
        """
        Atualiza os metadados do arquivo.
        
        Args:
            file_entity: Entidade do arquivo
            request: Dados de atualização
            
        Raises:
            FileValidationException: Se houver erro na atualização
        """
        try:
            logger.debug(f"Atualizando metadados do arquivo: {file_entity.file_id}")
            
            # Atualizar nome se fornecido
            if request.new_name is not None:
                old_name = file_entity.name.value
                file_entity.rename(request.new_name)
                logger.debug(f"Nome atualizado de '{old_name}' para '{request.new_name}'")
            
            # Atualizar descrição se fornecida
            if request.new_description is not None:
                file_entity.update_description(request.new_description)
                logger.debug(f"Descrição atualizada: {request.new_description}")
            
            # Atualizar tags se fornecidas
            if request.new_tags is not None:
                # Limpar tags existentes
                old_tags = [tag.value for tag in file_entity.tags]
                file_entity.clear_tags()
                
                # Adicionar novas tags
                for tag_value in request.new_tags:
                    tag = Tag(tag_value)
                    file_entity.add_tag(tag)
                
                logger.debug(f"Tags atualizadas de {old_tags} para {request.new_tags}")
            
            logger.debug("Metadados atualizados com sucesso na entidade")
            
        except ValueError as e:
            logger.error(f"Erro de validação ao atualizar metadados: {str(e)}")
            raise FileValidationException(f"Erro de validação: {str(e)}") from e
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar metadados: {str(e)}")
            raise FileValidationException("Erro interno ao atualizar metadados") from e