import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from dependency_injector.wiring import Provide, inject

from cloud_storage_app.application.dtos.file_dtos import (
    UploadFileInputDTO, FileUploadResponseDTO, entity_to_specific_dto
)
from cloud_storage_app.domain.entities import AudioFile, ImageFile, VideoFile
from cloud_storage_app.domain.value_objects import UserId, FileType
from cloud_storage_app.infrastructure.database.repositories import (
    AudioFileRepository, ImageFileRepository, VideoFileRepository
)
from cloud_storage_app.infrastructure.storage.s3_storage_service import S3StorageService
from cloud_storage_app.domain.exceptions import FileValidationException, FileUploadException

logger = logging.getLogger(__name__)

class UploadFileUseCase:
    """
    Use Case para upload de arquivos.
    
    Responsável por:
    1. Validar o arquivo e seus metadados
    2. Determinar o tipo de arquivo (áudio, imagem, vídeo)
    3. Criar a entidade apropriada com tags
    4. Fazer upload para o S3
    5. Salvar metadados no banco de dados
    """

    @inject
    def __init__(self):
        self._db_session = None
        self._storage_service = None
        self._audio_repository = None
        self._image_repository = None
        self._video_repository = None

    def _get_file_type(self, mime_type: str) -> FileType:
        """Determina o tipo de arquivo baseado no MIME type"""
        try:
            return FileType.from_mime_type(mime_type)
        except ValueError as e:
            raise FileValidationException(f"Tipo de arquivo não suportado: {mime_type}")

    def _create_file_entity(self, owner_id: UserId, upload_dto: UploadFileInputDTO, 
                           file_path: str, file_type: FileType):
        """Cria a entidade de arquivo apropriada baseada no tipo"""
        
        # Parâmetros comuns
        common_params = {
            'owner_id': owner_id,
            'name': upload_dto.file_name,
            'path': file_path,
            'size': upload_dto.file_size,
            'description': upload_dto.description or "",
            'tags': upload_dto.tags or []
        }
        
        # Criar entidade baseada na categoria
        if file_type.category.value == 'audio':
            return AudioFile.create(**common_params)
        elif file_type.category.value == 'image':
            return ImageFile.create(**common_params)
        elif file_type.category.value == 'video':
            return VideoFile.create(**common_params)
        else:
            raise FileValidationException(f"Categoria de arquivo não suportada: {file_type.category.value}")

    def _get_repository(self, file_type: FileType):
        """Retorna o repositório apropriado baseado no tipo de arquivo"""
        if file_type.category.value == 'audio':
            return self._audio_repository
        elif file_type.category.value == 'image':
            return self._image_repository
        elif file_type.category.value == 'video':
            return self._video_repository
        else:
            raise FileValidationException(f"Repositório não encontrado para categoria: {file_type.category.value}")

    async def execute(self, upload_dto: UploadFileInputDTO, owner_id: UserId, access_token: str, 
                     db_session: AsyncSession, storage_service: S3StorageService) -> FileUploadResponseDTO:
        """
        Executa o upload de arquivo.
        
        Args:
            upload_dto: DTO com dados do arquivo e tags
            owner_id: ID do usuário proprietário
            db_session: Sessão do banco de dados
            storage_service: Serviço de armazenamento
            
        Returns:
            FileUploadResponseDTO: Dados do arquivo criado
            
        Raises:
            FileValidationException: Se houver erro de validação
            FileUploadException: Se houver erro no upload
        """
        
        # Configurar dependências
        self._db_session = db_session
        self._storage_service = storage_service
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)
        
        logger.info(f"Iniciando upload do arquivo: {upload_dto.file_name}")
        logger.debug(f"Tags fornecidas: {upload_dto.tags}")

        try:

            

            # 1. Validar e determinar tipo de arquivo
            file_type = self._get_file_type(upload_dto.mime_type)
            logger.debug(f"Tipo de arquivo determinado: {file_type.category.value}")

            # 2. Criar caminho do arquivo
            # Aqui você implementaria a lógica para gerar o caminho baseado no tipo
            file_path = f"{owner_id.value}/{file_type.category.value}/{upload_dto.file_name}"

            # 3. Criar entidade de arquivo
            file_entity = self._create_file_entity(owner_id, upload_dto, file_path, file_type)
            logger.debug(f"Entidade criada com {len(file_entity.tags)} tags")

            # 4. Fazer upload para o S3
            await self._storage_service.upload_file(
                upload_dto.file_object,
                file_entity.path,
                upload_dto.mime_type
            )
            logger.info(f"Arquivo enviado para S3: {file_path}")

            # 5. Salvar no banco de dados
            repository = self._get_repository(file_type)
            await repository.save(file_entity)
            await self._db_session.commit()
            logger.info(f"Metadados salvos no banco: {file_entity.file_id}")

            # 6. Retornar resposta
            return FileUploadResponseDTO(
                file_id=str(file_entity.file_id.value),
                name=file_entity.name.value,
                description=file_entity.description.value if file_entity.description else None,
                file_type=file_entity.file_type.mime_type,
                mime_type=file_entity.file_type.mime_type,
                size=file_entity.size.value,
                size_humanized=str(file_entity.size),
                tags=[tag.value for tag in file_entity.tags],
                created_at=file_entity.created_at
            )

        except (FileValidationException, FileUploadException) as e:
            logger.error(f"Erro no upload: {str(e)}")
            await self._db_session.rollback()
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no upload: {str(e)}")
            await self._db_session.rollback()
            raise FileUploadException(f"Erro interno no upload: {str(e)}")
    