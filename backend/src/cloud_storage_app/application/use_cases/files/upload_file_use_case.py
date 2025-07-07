import logging
import io
import asyncio
import uuid
from typing import Optional, Dict, IO, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject
from datetime import date
from tempfile import SpooledTemporaryFile

from dependency_injector.wiring import Provide, inject

from cloud_storage_app.application.dtos.file_dtos import (
    UploadFileInputDTO, FileUploadResponseDTO, entity_to_specific_dto
)
from cloud_storage_app.domain.entities import AudioFile, ImageFile, VideoFile
from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.domain.value_objects import UserId, FileType, FilePath
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService, TokenPayload
from cloud_storage_app.infrastructure.database.repositories import (
    AudioFileRepository, ImageFileRepository, VideoFileRepository, UserRepository
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
from cloud_storage_app.infrastructure.storage.s3_storage_service import S3StorageService
from cloud_storage_app.infrastructure.external.audio_processing_service import MutagenAudioProcessingService
from cloud_storage_app.infrastructure.external.image_processing_service import PillowImageProcessingService
from cloud_storage_app.infrastructure.external.video_processing_service import FFmpegVideoProcessingService
from cloud_storage_app.infrastructure.external.thumbnail_generator_service import PillowThumbnailGeneratorService
from cloud_storage_app.domain.exceptions import FileValidationException, FileUploadException

logger = logging.getLogger(__name__)

class UploadFileUseCase:
    """
    Caso de uso para upload de arquivos com processamento de mídia.
    """

    @inject
    def __init__(
        self,
        audio_processing_service: MutagenAudioProcessingService,
        image_processing_service: PillowImageProcessingService,
        video_processing_service: FFmpegVideoProcessingService,
        thumbnail_generator_service: PillowThumbnailGeneratorService,
        jwt_service: JWTService,
    ):
        self._audio_processing_service = audio_processing_service
        self._image_processing_service = image_processing_service
        self._video_processing_service = video_processing_service
        self._thumbnail_generator_service = thumbnail_generator_service
        self._jwt_service = jwt_service
        self._db_session = None
        self._storage_service = None
        self._user_repository = None
        self._audio_repository = None
        self._image_repository = None
        self._video_repository = None
        logger.debug("UploadFileUseCase inicializado com serviços de processamento")

    async def execute(self, upload_dto: UploadFileInputDTO, access_token: str,
                     db_session: AsyncSession, storage_service: S3StorageService) -> FileUploadResponseDTO:
        """
        Orquestra o processo de upload, validação, processamento e armazenamento do arquivo.
        """
        self._setup_dependencies(db_session, storage_service)
        logger.info(f"Iniciando upload do arquivo: {upload_dto.file_name}")

        try:
            # 1. Autenticação e Autorização
            token_payload = await self._decode_and_validate_token(access_token)
            user = await self._find_user_by_id(token_payload.sub)
            self._check_user_status(user)

            # 2. Validação do Arquivo e Determinação do Tipo
            self._validate_request(upload_dto, access_token)
            file_data = await self._read_file_data(upload_dto.file_object)
            file_type = self._get_file_type(upload_dto.mime_type)
            logger.debug(f"Tipo de arquivo determinado: {file_type.category.value}")

            # 3. Processamento e Criação da Entidade
            if file_type.is_audio():
                file_entity = await self._process_audio_file(user.user_id, file_data, upload_dto)
            elif file_type.is_image():
                file_entity = await self._process_image_file(user.user_id, file_data, upload_dto)
            elif file_type.is_video():
                file_entity = await self._process_video_file(user.user_id, file_data, upload_dto)
            else:
                raise FileValidationException(f"Categoria de arquivo não suportada: {file_type.category.value}")

            # 4. Upload do Arquivo Principal
            await self._upload_main_file(file_data, file_entity.path, file_entity.mime_type)

            # 5. Persistência no Banco de Dados
            repository = self._get_repository(file_type)
            await repository.save(file_entity)
            await self._db_session.commit()
            logger.info(f"Metadados do arquivo salvos no BD: {file_entity.file_id}")

            # 6. Pós-processamento (ex: transcodificação de vídeo em background)
            # if file_type.is_video():
            #     # Em um sistema de produção, isso seria idealmente delegado a um worker (Celery, ARQ, etc.)
            #     asyncio.create_task(self._process_video_versions_task(video_entity=file_entity, video_data=file_data))

            # 7. Retorno do DTO de Resposta
            return entity_to_specific_dto(file_entity)

        except (FileValidationException, FileUploadException, AuthenticationException, UserNotFoundException, ValidationException) as e:
            logger.error(f"Falha no upload: {e}")
            await self._db_session.rollback()
            raise
        except Exception as e:
            logger.error(f"Erro inesperado durante o upload: {e}", exc_info=True)
            await self._db_session.rollback()
            raise FileUploadException(f"Ocorreu um erro interno durante o upload: {e}")

    # --- Métodos de Processamento por Tipo de Arquivo ---

    async def _process_audio_file(self, owner_id: UserId, file_data: bytes, upload_dto: UploadFileInputDTO) -> AudioFile:
        metadata = await self._audio_processing_service.extract_metadata(file_data, upload_dto.file_name)
        # Cria um caminho temporário que segue o padrão da validação
        temp_path = f"{owner_id.value}/audios/2025/07/07/temp_{uuid.uuid4().hex[:8]}/default/temp_{upload_dto.file_name}"
        
        file_entity = AudioFile.create(
            owner_id=owner_id, name=upload_dto.file_name, size=upload_dto.file_size,
            description=upload_dto.description, tags=upload_dto.tags, path=temp_path, **metadata
        )
        final_path = FilePath.create_audio(
            user_id=owner_id.value, file_id=file_entity.file_id.value, file_name=file_entity.name.value
        )
        file_entity.move(str(final_path))
        return file_entity

    async def _process_image_file(self, owner_id: UserId, file_data: bytes, upload_dto: UploadFileInputDTO) -> ImageFile:
        metadata = await self._image_processing_service.extract_metadata(file_data, upload_dto.file_name)
        # Cria um caminho temporário que segue o padrão da validação
        temp_path = f"{owner_id.value}/images/2025/07/07/temp_{uuid.uuid4().hex[:8]}/default/temp_{upload_dto.file_name}"
        
        file_entity = ImageFile.create(
             owner_id=owner_id, name=upload_dto.file_name, size=upload_dto.file_size,
             description=upload_dto.description, tags=upload_dto.tags, path=temp_path, **metadata
        )
        final_path = FilePath.create_image(
            user_id=owner_id.value, file_id=file_entity.file_id.value, file_name=file_entity.name.value
        )
        file_entity.move(str(final_path))
        
        thumbnail_data = await self._thumbnail_generator_service.generate_image_thumbnail(file_data)
        if thumbnail_data:
            thumb_path = file_entity.generate_thumbnail_path()
            await self._storage_service.upload_file(io.BytesIO(thumbnail_data), thumb_path, 'image/jpeg')
            file_entity.set_thumbnail(str(thumb_path))
        return file_entity

    async def _process_video_file(self, owner_id: UserId, file_data: bytes, upload_dto: UploadFileInputDTO) -> VideoFile:
        metadata = await self._video_processing_service.extract_video_metadata(file_data)
        original_resolution = self._video_processing_service._height_to_quality(metadata.get('height', 0))
        
        # Cria um caminho temporário que segue o padrão da validação
        temp_path = f"{owner_id.value}/videos/2025/07/07/temp_{uuid.uuid4().hex[:8]}/original/temp_{upload_dto.file_name}"
        
        file_entity = VideoFile.create(
            owner_id=owner_id, name=upload_dto.file_name, size=upload_dto.file_size,
            description=upload_dto.description, tags=upload_dto.tags, path=temp_path, 
            original_resolution=original_resolution, **metadata
        )

        original_path = FilePath.create_video(
            user_id=owner_id.value, file_id=file_entity.file_id.value,
            resolution='original', file_name=file_entity.name.value
        )
        file_entity.move(str(original_path))
        file_entity.update_version_status(original_resolution, 'completed')

        thumbnail_data = await self._thumbnail_generator_service.generate_video_thumbnail(file_data)
        if thumbnail_data:
            thumb_path = file_entity.generate_thumbnail_path()
            await self._storage_service.upload_file(io.BytesIO(thumbnail_data), thumb_path, 'image/jpeg')
            file_entity.set_thumbnail(str(thumb_path))
        return file_entity

    # --- Métodos Auxiliares ---

    def _setup_dependencies(self, db_session: AsyncSession, storage_service: S3StorageService):
        self._db_session = db_session
        self._storage_service = storage_service
        self._user_repository = UserRepository(session=db_session)
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)

    async def _read_file_data(self, file_object: Union[IO[Any], SpooledTemporaryFile]) -> bytes:
        # Verifica se é um objeto assíncrono ou síncrono
        if hasattr(file_object, 'read') and asyncio.iscoroutinefunction(file_object.read):
            # Objeto assíncrono
            file_data = await file_object.read()
            await file_object.seek(0)
        else:
            # Objeto síncrono (como SpooledTemporaryFile do FastAPI)
            file_data = file_object.read()
            file_object.seek(0)
        return file_data

    async def _upload_main_file(self, file_data: bytes, file_path: FilePath, mime_type: str):
        try:
            await self._storage_service.upload_file(io.BytesIO(file_data), file_path, mime_type)
            logger.info(f"Arquivo enviado para o S3: {file_path}")
        except Exception as e:
            raise FileUploadException(f"Falha ao enviar o arquivo principal para o armazenamento: {e}")

    async def _process_video_versions_task(self, video_entity: VideoFile, video_data: bytes):
        logger.info(f"Iniciando processamento de vídeo em background para: {video_entity.file_id.value}")
        target_qualities = ['1080p', '720p', '480p']
        
        # A implementação atual de `process_video_quality_versions` precisa ser adaptada
        # para não salvar arquivos localmente, mas sim retorná-los ou fazer o upload direto.
        # Para este exemplo, vamos assumir que o serviço de vídeo lida com o upload.
        
        processed_versions = await self._video_processing_service.process_video_quality_versions(
            video_data=video_data,
            original_metadata={'height': video_entity.height},
            target_qualities=target_qualities,
            user_id=video_entity.owner_id.value,
            file_id=video_entity.file_id.value,
        )

        for quality, version in processed_versions.items():
            video_entity.add_version(version)

        # Para atualizar o BD em uma task de background, precisaríamos de uma nova sessão.
        # Isso destaca a necessidade de um gerenciador de dependências/sessões mais robusto
        # quando se trabalha com tarefas assíncronas.
        logger.info(f"Processamento de vídeo em background concluído para: {video_entity.file_id.value}")
        # Em um cenário real, aqui você faria o update no banco de dados.

    def _get_file_type(self, mime_type: str) -> FileType:
        try:
            return FileType.from_mime_type(mime_type)
        except ValueError as e:
            raise FileValidationException(f"Tipo de arquivo não suportado: {mime_type}") from e
    
    def _get_repository(self, file_type: FileType):
        if file_type.is_audio(): return self._audio_repository
        if file_type.is_image(): return self._image_repository
        if file_type.is_video(): return self._video_repository
        raise FileValidationException(f"Repositório não encontrado para categoria: {file_type.category.value}")

    def _validate_request(self, request: UploadFileInputDTO, access_token: str) -> None:
        """
        Valida os dados de entrada do request.
        
        Args:
            request: Request com parâmetros de listagem
            access_token: Token JWT de acesso
            
        Raises:
            AuthenticationException: Se o token estiver inválido
            ValidationException: Se os parâmetros de listagem forem inválidos
        """
        if not access_token or not access_token.strip():
            logger.warning("Token de acesso não fornecido")
            raise AuthenticationException("Token de acesso é obrigatório")
        
        # Verificar formato básico do token
        token_parts = access_token.strip().split('.')
        if len(token_parts) != 3:
            logger.warning("Token de acesso com formato inválido")
            raise AuthenticationException("Formato de token inválido")
        
        if not request.file_name:
            logger.warning()
            raise ValidationException("É necessário o nome do arquivo")
        
        if len(request.file_name) <= 1 or len(request.file_name) >= 255:
            logger.warning("Nome do arquivo deve ser menor que 255 caracterese maior ou igual aa 1")
            raise ValidationException("É necessário o nome do arquivo")

        if not request.file_size:
            logger.warning("É necessário o tamanho do arquivo")
            raise ValidationException("É necessário o tamanho do arquivo")

        if not request.mime_type:
            logger.warning("É necessário o tipo MIME do arquivo")
            raise ValidationException("É necessário o tipo MIME do arquivo")
        
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
            logger.warning(f"Tentativa de listagem com usuário inativo: {user.username.value}")
            raise AuthenticationException("Usuário inativo")
        
        logger.debug(f"Status do usuário {user.username.value} verificado com sucesso")
