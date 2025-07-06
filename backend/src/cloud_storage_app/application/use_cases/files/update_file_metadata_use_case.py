import logging
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.application.dtos.file_dtos import (
    UpdateFileMetadataInputDTO, FileResponseDTO, entity_to_specific_dto
)
from cloud_storage_app.domain.value_objects import FileId, UserId
from cloud_storage_app.infrastructure.database.repositories import (
    AudioFileRepository, ImageFileRepository, VideoFileRepository
)
from cloud_storage_app.domain.exceptions import FileNotFoundException, FileValidationException

logger = logging.getLogger(__name__)

class UpdateFileMetadataUseCase:
    """
    Use Case para atualização de metadados de arquivos.
    
    Responsável por:
    1. Buscar o arquivo no banco de dados
    2. Validar se o usuário tem permissão
    3. Atualizar os metadados (nome, descrição, tags)
    4. Salvar as alterações
    """

    def __init__(self):
        self._db_session = None
        self._audio_repository = None
        self._image_repository = None
        self._video_repository = None

    async def _find_file(self, file_id: FileId, owner_id: UserId):
        """Busca o arquivo em todos os repositórios"""
        # Tentar encontrar em cada repositório
        file_entity = None
        
        # Buscar em áudio
        file_entity = await self._audio_repository.find_by_id(file_id)
        if file_entity and file_entity.owner_id == owner_id:
            return file_entity, self._audio_repository
        
        # Buscar em imagem
        file_entity = await self._image_repository.find_by_id(file_id)
        if file_entity and file_entity.owner_id == owner_id:
            return file_entity, self._image_repository
        
        # Buscar em vídeo
        file_entity = await self._video_repository.find_by_id(file_id)
        if file_entity and file_entity.owner_id == owner_id:
            return file_entity, self._video_repository
        
        return None, None

    async def execute(self, update_dto: UpdateFileMetadataInputDTO, owner_id: UserId, 
                     db_session: AsyncSession) -> FileResponseDTO:
        """
        Executa a atualização de metadados do arquivo.
        
        Args:
            update_dto: DTO com os novos metadados
            owner_id: ID do usuário proprietário
            db_session: Sessão do banco de dados
            
        Returns:
            FileResponseDTO: Dados atualizados do arquivo
            
        Raises:
            FileNotFoundException: Se o arquivo não for encontrado
            FileValidationException: Se houver erro de validação
        """
        
        # Configurar dependências
        self._db_session = db_session
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)
        
        file_id = FileId.from_string(update_dto.file_id)
        
        logger.info(f"Iniciando atualização do arquivo: {file_id}")
        logger.debug(f"Novos metadados: name={update_dto.new_name}, description={update_dto.new_description}, tags={update_dto.new_tags}")

        try:
            # 1. Buscar o arquivo
            file_entity, repository = await self._find_file(file_id, owner_id)
            
            if not file_entity:
                raise FileNotFoundException(f"Arquivo não encontrado: {file_id}")
            
            if file_entity.is_deleted:
                raise FileValidationException("Não é possível atualizar um arquivo deletado")
            
            logger.debug(f"Arquivo encontrado: {file_entity.name.value}")

            # 2. Atualizar metadados
            if update_dto.new_name is not None:
                file_entity.rename(update_dto.new_name)
                logger.debug(f"Nome atualizado para: {update_dto.new_name}")
            
            if update_dto.new_description is not None:
                file_entity.update_description(update_dto.new_description)
                logger.debug(f"Descrição atualizada")
            
            if update_dto.new_tags is not None:
                # Limpar tags existentes e adicionar as novas
                file_entity.clear_tags()
                for tag in update_dto.new_tags:
                    from cloud_storage_app.domain.value_objects import Tag
                    file_entity.add_tag(Tag(tag))
                logger.debug(f"Tags atualizadas: {len(update_dto.new_tags)} tags")

            # 3. Salvar alterações
            await repository.save(file_entity)
            await self._db_session.commit()
            logger.info(f"Metadados atualizados com sucesso: {file_id}")

            # 4. Retornar resposta
            return entity_to_specific_dto(file_entity)

        except (FileNotFoundException, FileValidationException) as e:
            logger.error(f"Erro na atualização: {str(e)}")
            await self._db_session.rollback()
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na atualização: {str(e)}")
            await self._db_session.rollback()
            raise FileValidationException(f"Erro interno na atualização: {str(e)}")
