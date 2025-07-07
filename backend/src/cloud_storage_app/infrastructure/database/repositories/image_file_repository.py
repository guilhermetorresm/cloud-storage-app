from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from cloud_storage_app.domain.repositories.image_file_repository import ImageFileRepositoryInterface
from cloud_storage_app.domain.entities.image_file import ImageFile
from cloud_storage_app.domain.value_objects import FileId, UserId
from cloud_storage_app.infrastructure.database.models import ImageFileModel

import logging
logger = logging.getLogger(__name__)


class ImageFileRepository(ImageFileRepositoryInterface):
    """
    Implementação concreta do repositório de arquivos de imagem.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, image_file: ImageFile) -> None:
        """Salva ou atualiza um arquivo de imagem."""
        try:
            # Buscar se já existe no banco
            existing_model = await self._session.get(ImageFileModel, image_file.file_id.value)
            logger.info(f"Buscando arquivo no banco: {image_file.file_id.value}")
            
            if existing_model:
                logger.info(f"Arquivo encontrado, atualizando dados: {image_file.name.value}")
                # Atualizar arquivo existente
                existing_model.name = image_file.name.value
                existing_model.description = image_file.description.value
                existing_model.path = image_file.path.value
                existing_model.mime_type = image_file.file_type.mime_type
                existing_model.extension = image_file.file_type.extension
                existing_model.category = image_file.file_type.category.value
                existing_model.size = image_file.size.value
                existing_model.tags = ",".join([tag.value for tag in image_file.tags]) if image_file.tags else None
                existing_model.width = image_file.width
                existing_model.height = image_file.height
                existing_model.color_depth = image_file.color_depth
                existing_model.dpi = image_file.dpi
                existing_model.has_transparency = image_file.has_transparency
                existing_model.compression = image_file.compression
                existing_model.camera_make = image_file.camera_make
                existing_model.camera_model = image_file.camera_model
                existing_model.taken_at = image_file.taken_at
                existing_model.gps_latitude = image_file.gps_latitude
                existing_model.gps_longitude = image_file.gps_longitude
                existing_model.thumbnail = image_file.thumbnail.value if image_file.thumbnail else None
                existing_model.is_deleted = image_file.is_deleted
                existing_model.updated_at = image_file.updated_at
                existing_model.last_accessed_at = image_file.last_accessed_at
                
                logger.info(f"Dados atualizados: name={existing_model.name}, dimensions={existing_model.width}x{existing_model.height}")
            else:
                logger.info(f"Arquivo não encontrado, criando novo: {image_file.name.value}")
                # Criar novo arquivo
                image_file_model = ImageFileModel(
                    id=image_file.file_id.value,
                    owner_id=image_file.owner_id.value,
                    name=image_file.name.value,
                    description=image_file.description.value,
                    path=image_file.path.value,
                    mime_type=image_file.file_type.mime_type,
                    extension=image_file.file_type.extension,
                    category=image_file.file_type.category.value,
                    size=image_file.size.value,
                    tags=",".join([tag.value for tag in image_file.tags]) if image_file.tags else None,
                    width=image_file.width,
                    height=image_file.height,
                    color_depth=image_file.color_depth,
                    dpi=image_file.dpi,
                    has_transparency=image_file.has_transparency,
                    compression=image_file.compression,
                    camera_make=image_file.camera_make,
                    camera_model=image_file.camera_model,
                    taken_at=image_file.taken_at,
                    gps_latitude=image_file.gps_latitude,
                    gps_longitude=image_file.gps_longitude,
                    thumbnail=image_file.thumbnail.value if image_file.thumbnail else None,
                    is_deleted=image_file.is_deleted,
                    created_at=image_file.created_at,
                    updated_at=image_file.updated_at,
                    last_accessed_at=image_file.last_accessed_at
                )
                self._session.add(image_file_model)
                logger.info(f"Novo arquivo criado: {image_file_model.name}")
            
            # Salvar alterações
            await self._session.flush()
            await self._session.commit()
            logger.info(f"Alterações salvas com sucesso para o arquivo: {image_file.name.value}")
            
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao salvar arquivo: {str(e)}")
            await self._session.rollback()
            raise ValueError(f"Erro ao salvar arquivo: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar arquivo: {str(e)}")
            await self._session.rollback()
            raise ValueError(f"Erro ao salvar arquivo: {str(e)}")
        
    async def find_by_id(self, file_id: FileId) -> Optional[ImageFile]:
        """Busca arquivo por ID."""
        stmt = select(ImageFileModel).where(ImageFileModel.id == file_id.value)
        result = await self._session.execute(stmt)
        image_file_model = result.scalar_one_or_none()
        
        if image_file_model:
            return self._model_to_entity(image_file_model)
        return None

    async def find_by_owner_id(self, owner_id: UserId) -> List[ImageFile]:
        """Busca arquivos por proprietário."""
        stmt = (
            select(ImageFileModel)
            .where(ImageFileModel.owner_id == owner_id.value)
            .where(ImageFileModel.is_deleted == False)
            .order_by(ImageFileModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        image_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in image_file_models]

    async def find_by_name_and_owner(self, name: str, owner_id: UserId) -> Optional[ImageFile]:
        """Busca arquivo por nome e proprietário."""
        stmt = (
            select(ImageFileModel)
            .where(ImageFileModel.name == name)
            .where(ImageFileModel.owner_id == owner_id.value)
            .where(ImageFileModel.is_deleted == False)
        )
        result = await self._session.execute(stmt)
        image_file_model = result.scalar_one_or_none()
        
        if image_file_model:
            return self._model_to_entity(image_file_model)
        return None

    async def find_by_tags(self, tags: List[str], owner_id: UserId) -> List[ImageFile]:
        """Busca arquivos por tags."""
        stmt = (
            select(ImageFileModel)
            .where(ImageFileModel.owner_id == owner_id.value)
            .where(ImageFileModel.is_deleted == False)
        )
        
        # Filtrar por tags (busca por substring nas tags)
        for tag in tags:
            stmt = stmt.where(ImageFileModel.tags.contains(tag))
        
        stmt = stmt.order_by(ImageFileModel.created_at.desc())
        result = await self._session.execute(stmt)
        image_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in image_file_models]

    async def delete(self, file_id: FileId) -> None:
        """Remove um arquivo (soft delete)."""
        stmt = (
            update(ImageFileModel)
            .where(ImageFileModel.id == file_id.value)
            .values(is_deleted=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def find_all_active(self, limit: int = 100, offset: int = 0) -> List[ImageFile]:
        """Lista arquivos ativos com paginação."""
        stmt = (
            select(ImageFileModel)
            .where(ImageFileModel.is_deleted == False)
            .offset(offset)
            .limit(limit)
            .order_by(ImageFileModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        image_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in image_file_models]

    def _model_to_entity(self, model: ImageFileModel) -> ImageFile:
        """Converte ImageFileModel para ImageFile entity."""
        from cloud_storage_app.domain.value_objects import (
            FileId, UserId, FileName, FileSize, FilePath, FileType, FileCategory,
            FileDescription, Tag
        )
        
        # Criar instância ImageFile diretamente com os atributos privados
        image_file = ImageFile.__new__(ImageFile)  # Criar sem chamar __init__
        
        # Definir atributos privados diretamente
        image_file._file_id = FileId.from_string(model.id)
        image_file._owner_id = UserId.from_string(model.owner_id)
        image_file._name = FileName(model.name)
        image_file._description = FileDescription(model.description)
        image_file._path = FilePath(model.path)
        image_file._file_type = FileType(
            mime_type=model.mime_type,
            extension=model.extension,
            category=FileCategory(model.category)
        )
        image_file._size = FileSize(model.size)
        image_file._tags = [Tag(tag.strip()) for tag in model.tags.split(",")] if model.tags else []
        image_file._width = model.width
        image_file._height = model.height
        image_file._color_depth = model.color_depth
        image_file._dpi = model.dpi
        image_file._has_transparency = model.has_transparency
        image_file._compression = model.compression
        image_file._camera_make = model.camera_make
        image_file._camera_model = model.camera_model
        image_file._taken_at = model.taken_at
        image_file._gps_latitude = model.gps_latitude
        image_file._gps_longitude = model.gps_longitude
        image_file._thumbnail = FilePath(model.thumbnail) if model.thumbnail else None
        image_file._is_deleted = model.is_deleted
        image_file._created_at = model.created_at
        image_file._updated_at = model.updated_at
        image_file._last_accessed_at = model.last_accessed_at
        image_file._domain_events = []
        
        return image_file