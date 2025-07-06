import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.application.dtos.file_dtos import (
    ListUserFilesInputDTO, FileListResponseDTO, FileResponseDTO,
    entity_to_file_response_dto
)
from cloud_storage_app.domain.value_objects import UserId
from cloud_storage_app.infrastructure.database.repositories import (
    AudioFileRepository, ImageFileRepository, VideoFileRepository
)
from cloud_storage_app.domain.exceptions import FileValidationException

logger = logging.getLogger(__name__)

class ListUserFilesUseCase:
    """
    Use Case para listagem de arquivos do usuário.
    
    Responsável por:
    1. Buscar arquivos do usuário com filtros
    2. Aplicar paginação
    3. Filtrar por tipo de arquivo e tags
    4. Retornar lista paginada
    """

    def __init__(self):
        self._db_session = None
        self._audio_repository = None
        self._image_repository = None
        self._video_repository = None

    def _entity_to_dto(self, file_entity) -> FileResponseDTO:
        """Converte entidade de arquivo para DTO específico"""
        return entity_to_file_response_dto(file_entity)

    async def execute(self, list_dto: ListUserFilesInputDTO, db_session: AsyncSession) -> FileListResponseDTO:
        """
        Executa a listagem de arquivos do usuário.
        
        Args:
            list_dto: DTO com parâmetros de listagem e filtros
            db_session: Sessão do banco de dados
            
        Returns:
            FileListResponseDTO: Lista paginada de arquivos
            
        Raises:
            FileValidationException: Se houver erro de validação
        """
        
        # Configurar dependências
        self._db_session = db_session
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)
        
        owner_id = UserId.from_string(list_dto.user_id)
        
        logger.info(f"Listando arquivos do usuário: {owner_id}")
        logger.debug(f"Filtros: type={list_dto.file_type}, tags={list_dto.tags}, name={list_dto.file_name}")

        try:
            all_files = []
            
            # 1. Buscar arquivos baseado no tipo
            if list_dto.file_type is None or list_dto.file_type == 'audio':
                audio_files = await self._audio_repository.find_by_owner_id(owner_id)
                all_files.extend(audio_files)
                logger.debug(f"Encontrados {len(audio_files)} arquivos de áudio")
            
            if list_dto.file_type is None or list_dto.file_type == 'image':
                image_files = await self._image_repository.find_by_owner_id(owner_id)
                all_files.extend(image_files)
                logger.debug(f"Encontrados {len(image_files)} arquivos de imagem")
            
            if list_dto.file_type is None or list_dto.file_type == 'video':
                video_files = await self._video_repository.find_by_owner_id(owner_id)
                all_files.extend(video_files)
                logger.debug(f"Encontrados {len(video_files)} arquivos de vídeo")

            # 2. Aplicar filtros
            filtered_files = []
            
            for file_entity in all_files:
                # Filtrar por nome (se especificado)
                if list_dto.file_name and list_dto.file_name.lower() not in file_entity.name.value.lower():
                    continue
                
                # Filtrar por tags (se especificado)
                if list_dto.tags:
                    file_tags = [tag.value.lower() for tag in file_entity.tags]
                    filter_tags = [tag.lower() for tag in list_dto.tags]
                    
                    # Verificar se pelo menos uma tag de filtro está presente no arquivo
                    if not any(filter_tag in file_tag for filter_tag in filter_tags for file_tag in file_tags):
                        continue
                
                filtered_files.append(file_entity)
            
            logger.debug(f"Após filtros: {len(filtered_files)} arquivos")

            # 3. Ordenar por data de criação (mais recentes primeiro)
            filtered_files.sort(key=lambda x: x.created_at, reverse=True)

            # 4. Aplicar paginação
            total_count = len(filtered_files)
            start_index = (list_dto.page - 1) * list_dto.page_size
            end_index = start_index + list_dto.page_size
            paginated_files = filtered_files[start_index:end_index]
            
            total_pages = (total_count + list_dto.page_size - 1) // list_dto.page_size

            # 5. Converter para DTOs
            file_dtos = [self._entity_to_dto(file_entity) for file_entity in paginated_files]

            logger.info(f"Retornando {len(file_dtos)} arquivos da página {list_dto.page}")

            # 6. Retornar resposta
            return FileListResponseDTO(
                files=file_dtos,
                total_count=total_count,
                page=list_dto.page,
                page_size=list_dto.page_size,
                total_pages=total_pages
            )

        except Exception as e:
            logger.error(f"Erro na listagem: {str(e)}")
            raise FileValidationException(f"Erro interno na listagem: {str(e)}")
