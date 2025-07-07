from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from cloud_storage_app.domain.repositories.video_file_repository import VideoFileRepositoryInterface
from cloud_storage_app.domain.entities.video_file import VideoFile
from cloud_storage_app.domain.value_objects import FileId, UserId
from cloud_storage_app.infrastructure.database.models import VideoFileModel

import logging
logger = logging.getLogger(__name__)


class VideoFileRepository(VideoFileRepositoryInterface):
    """
    Implementação concreta do repositório de arquivos de vídeo.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, video_file: VideoFile) -> None:
        """Salva ou atualiza um arquivo de vídeo."""
        try:
            # Buscar se já existe no banco
            existing_model = await self._session.get(VideoFileModel, video_file.file_id.value)
            logger.info(f"Buscando arquivo no banco: {video_file.file_id.value}")
            
            if existing_model:
                logger.info(f"Arquivo encontrado, atualizando dados: {video_file.name.value}")
                # Atualizar arquivo existente
                existing_model.name = video_file.name.value
                existing_model.description = video_file.description.value
                existing_model.path = video_file.path.value
                existing_model.mime_type = video_file.file_type.mime_type
                existing_model.extension = video_file.file_type.extension
                existing_model.category = video_file.file_type.category.value
                existing_model.size = video_file.size.value
                existing_model.tags = ",".join([tag.value for tag in video_file.tags]) if video_file.tags else None
                existing_model.duration_seconds = video_file.duration_seconds
                existing_model.width = video_file.width
                existing_model.height = video_file.height
                existing_model.frame_rate = video_file.frame_rate
                existing_model.bitrate = video_file.bitrate
                existing_model.codec = video_file.codec
                existing_model.audio_codec = video_file.audio_codec
                existing_model.has_audio = video_file.has_audio
                existing_model.has_subtitles = video_file.has_subtitles
                existing_model.created_with = video_file.created_with
                existing_model.genre = video_file._genre
                existing_model.thumbnail = video_file.thumbnail.value if video_file.thumbnail else None
                existing_model.versions = self._serialize_versions(video_file._versions)
                existing_model.original_version = video_file._original_version
                existing_model.is_deleted = video_file.is_deleted
                existing_model.updated_at = video_file.updated_at
                existing_model.last_accessed_at = video_file.last_accessed_at
                
                logger.info(f"Dados atualizados: name={existing_model.name}, duration={existing_model.duration_seconds}s")
            else:
                logger.info(f"Arquivo não encontrado, criando novo: {video_file.name.value}")
                # Criar novo arquivo
                video_file_model = VideoFileModel(
                    id=video_file.file_id.value,
                    owner_id=video_file.owner_id.value,
                    name=video_file.name.value,
                    description=video_file.description.value,
                    path=video_file.path.value,
                    mime_type=video_file.file_type.mime_type,
                    extension=video_file.file_type.extension,
                    category=video_file.file_type.category.value,
                    size=video_file.size.value,
                    tags=",".join([tag.value for tag in video_file.tags]) if video_file.tags else None,
                    duration_seconds=video_file.duration_seconds,
                    width=video_file.width,
                    height=video_file.height,
                    frame_rate=video_file.frame_rate,
                    bitrate=video_file.bitrate,
                    codec=video_file.codec,
                    audio_codec=video_file.audio_codec,
                    has_audio=video_file.has_audio,
                    has_subtitles=video_file.has_subtitles,
                    created_with=video_file.created_with,
                    genre=video_file._genre,
                    thumbnail=video_file.thumbnail.value if video_file.thumbnail else None,
                    versions=self._serialize_versions(video_file._versions),
                    original_version=video_file._original_version,
                    is_deleted=video_file.is_deleted,
                    created_at=video_file.created_at,
                    updated_at=video_file.updated_at,
                    last_accessed_at=video_file.last_accessed_at
                )
                self._session.add(video_file_model)
                logger.info(f"Novo arquivo criado: {video_file_model.name}")
            
            # Salvar alterações
            await self._session.flush()
            await self._session.commit()
            logger.info(f"Alterações salvas com sucesso para o arquivo: {video_file.name.value}")
            
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao salvar arquivo: {str(e)}")
            await self._session.rollback()
            raise ValueError(f"Erro ao salvar arquivo: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar arquivo: {str(e)}")
            await self._session.rollback()
            raise ValueError(f"Erro ao salvar arquivo: {str(e)}")
        
    async def find_by_id(self, file_id: FileId) -> Optional[VideoFile]:
        """Busca arquivo por ID."""
        stmt = select(VideoFileModel).where(VideoFileModel.id == file_id.value)
        result = await self._session.execute(stmt)
        video_file_model = result.scalar_one_or_none()
        
        if video_file_model:
            return self._model_to_entity(video_file_model)
        return None

    async def find_by_owner_id(self, owner_id: UserId) -> List[VideoFile]:
        """Busca arquivos por proprietário."""
        stmt = (
            select(VideoFileModel)
            .where(VideoFileModel.owner_id == owner_id.value)
            .where(VideoFileModel.is_deleted == False)
            .order_by(VideoFileModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        video_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in video_file_models]

    async def find_by_name_and_owner(self, name: str, owner_id: UserId) -> Optional[VideoFile]:
        """Busca arquivo por nome e proprietário."""
        stmt = (
            select(VideoFileModel)
            .where(VideoFileModel.name == name)
            .where(VideoFileModel.owner_id == owner_id.value)
            .where(VideoFileModel.is_deleted == False)
        )
        result = await self._session.execute(stmt)
        video_file_model = result.scalar_one_or_none()
        
        if video_file_model:
            return self._model_to_entity(video_file_model)
        return None

    async def find_by_tags(self, tags: List[str], owner_id: UserId) -> List[VideoFile]:
        """Busca arquivos por tags."""
        stmt = (
            select(VideoFileModel)
            .where(VideoFileModel.owner_id == owner_id.value)
            .where(VideoFileModel.is_deleted == False)
        )
        
        # Filtrar por tags (busca por substring nas tags)
        for tag in tags:
            stmt = stmt.where(VideoFileModel.tags.contains(tag))
        
        stmt = stmt.order_by(VideoFileModel.created_at.desc())
        result = await self._session.execute(stmt)
        video_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in video_file_models]

    async def find_by_duration_range(self, min_duration: Optional[int], max_duration: Optional[int], 
                                   owner_id: UserId) -> List[VideoFile]:
        """Busca arquivos por intervalo de duração."""
        stmt = (
            select(VideoFileModel)
            .where(VideoFileModel.owner_id == owner_id.value)
            .where(VideoFileModel.is_deleted == False)
        )
        
        if min_duration is not None:
            stmt = stmt.where(VideoFileModel.duration_seconds >= min_duration)
        if max_duration is not None:
            stmt = stmt.where(VideoFileModel.duration_seconds <= max_duration)
        
        stmt = stmt.order_by(VideoFileModel.created_at.desc())
        result = await self._session.execute(stmt)
        video_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in video_file_models]

    async def find_by_resolution(self, min_width: Optional[int], max_width: Optional[int],
                               min_height: Optional[int], max_height: Optional[int],
                               owner_id: UserId) -> List[VideoFile]:
        """Busca arquivos por resolução."""
        stmt = (
            select(VideoFileModel)
            .where(VideoFileModel.owner_id == owner_id.value)
            .where(VideoFileModel.is_deleted == False)
        )
        
        if min_width is not None:
            stmt = stmt.where(VideoFileModel.width >= min_width)
        if max_width is not None:
            stmt = stmt.where(VideoFileModel.width <= max_width)
        if min_height is not None:
            stmt = stmt.where(VideoFileModel.height >= min_height)
        if max_height is not None:
            stmt = stmt.where(VideoFileModel.height <= max_height)
        
        stmt = stmt.order_by(VideoFileModel.created_at.desc())
        result = await self._session.execute(stmt)
        video_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in video_file_models]

    async def find_by_codec(self, codec: str, owner_id: UserId) -> List[VideoFile]:
        """Busca arquivos por codec."""
        stmt = (
            select(VideoFileModel)
            .where(VideoFileModel.owner_id == owner_id.value)
            .where(VideoFileModel.is_deleted == False)
            .where(VideoFileModel.codec == codec)
            .order_by(VideoFileModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        video_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in video_file_models]

    async def delete(self, file_id: FileId) -> None:
        """Remove um arquivo (soft delete)."""
        stmt = (
            update(VideoFileModel)
            .where(VideoFileModel.id == file_id.value)
            .values(is_deleted=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def find_all_active(self, limit: int = 100, offset: int = 0) -> List[VideoFile]:
        """Lista arquivos ativos com paginação."""
        stmt = (
            select(VideoFileModel)
            .where(VideoFileModel.is_deleted == False)
            .offset(offset)
            .limit(limit)
            .order_by(VideoFileModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        video_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in video_file_models]

    def _serialize_versions(self, versions: dict) -> dict:
        """Serializa as versões do vídeo para JSON."""
        if not versions:
            return {}
        
        serialized = {}
        for resolution, version in versions.items():
            serialized[resolution] = {
                'resolution': version.resolution,
                'file_path': str(version.file_path),
                'is_original': version.is_original,
                'processing_status': version.processing_status
            }
        return serialized

    def _deserialize_versions(self, versions_data: dict):
        """Deserializa as versões do vídeo do JSON."""
        if not versions_data:
            return {}
        
        from cloud_storage_app.domain.value_objects import VideoVersion, FilePath
        
        versions = {}
        for resolution, version_data in versions_data.items():
            versions[resolution] = VideoVersion(
                resolution=version_data['resolution'],
                file_path=FilePath(version_data['file_path']),
                is_original=version_data['is_original'],
                processing_status=version_data['processing_status']
            )
        return versions

    def _model_to_entity(self, model: VideoFileModel) -> VideoFile:
        """Converte VideoFileModel para VideoFile entity."""
        from cloud_storage_app.domain.value_objects import (
            FileId, UserId, FileName, FileSize, FilePath, FileType, FileCategory,
            FileDescription, Tag
        )
        
        # Criar instância VideoFile diretamente com os atributos privados
        video_file = VideoFile.__new__(VideoFile)  # Criar sem chamar __init__
        
        # Definir atributos privados diretamente
        video_file._file_id = FileId.from_string(model.id)
        video_file._owner_id = UserId.from_string(model.owner_id)
        video_file._name = FileName(model.name)
        video_file._description = FileDescription(model.description)
        video_file._path = FilePath(model.path)
        video_file._file_type = FileType(
            mime_type=model.mime_type,
            extension=model.extension,
            category=FileCategory(model.category)
        )
        video_file._size = FileSize(model.size)
        video_file._tags = [Tag(tag.strip()) for tag in model.tags.split(",")] if model.tags else []
        video_file._duration_seconds = model.duration_seconds
        video_file._width = model.width
        video_file._height = model.height
        video_file._frame_rate = model.frame_rate
        video_file._bitrate = model.bitrate
        video_file._codec = model.codec
        video_file._audio_codec = model.audio_codec
        video_file._has_audio = model.has_audio
        video_file._has_subtitles = model.has_subtitles
        video_file._created_with = model.created_with
        video_file._genre = model.genre
        video_file._thumbnail = FilePath(model.thumbnail) if model.thumbnail else None
        video_file._versions = self._deserialize_versions(model.versions)
        video_file._original_version = model.original_version
        video_file._is_deleted = model.is_deleted
        video_file._created_at = model.created_at
        video_file._updated_at = model.updated_at
        video_file._last_accessed_at = model.last_accessed_at
        video_file._domain_events = []
        
        return video_file