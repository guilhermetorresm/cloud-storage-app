from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from cloud_storage_app.domain.repositories.audio_file_repository import AudioFileRepositoryInterface
from cloud_storage_app.domain.entities.audio_file import AudioFile
from cloud_storage_app.domain.value_objects import FileId, UserId
from cloud_storage_app.infrastructure.database.models import AudioFileModel

import logging
logger = logging.getLogger(__name__)


class AudioFileRepository(AudioFileRepositoryInterface):
    """
    Implementação concreta do repositório de arquivos de áudio.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, audio_file: AudioFile) -> None:
        """Salva ou atualiza um arquivo de áudio."""
        try:
            # Buscar se já existe no banco
            existing_model = await self._session.get(AudioFileModel, audio_file.file_id.value)
            logger.info(f"Buscando arquivo no banco: {audio_file.file_id.value}")
            
            if existing_model:
                logger.info(f"Arquivo encontrado, atualizando dados: {audio_file.name.value}")
                # Atualizar arquivo existente
                existing_model.name = audio_file.name.value
                existing_model.description = audio_file.description.value
                existing_model.path = audio_file.path.value
                existing_model.mime_type = audio_file.file_type.mime_type
                existing_model.extension = audio_file.file_type.extension
                existing_model.category = audio_file.file_type.category.value
                existing_model.size = audio_file.size.value
                existing_model.tags = ",".join([tag.value for tag in audio_file.tags]) if audio_file.tags else None
                existing_model.duration_seconds = audio_file.duration_seconds
                existing_model.bitrate = audio_file.bitrate
                existing_model.sample_rate = audio_file.sample_rate
                existing_model.channels = audio_file.channels
                existing_model.genre = audio_file.genre
                existing_model.is_deleted = audio_file.is_deleted
                existing_model.updated_at = audio_file.updated_at
                existing_model.last_accessed_at = audio_file.last_accessed_at
                
                logger.info(f"Dados atualizados: name={existing_model.name}, duration={existing_model.duration_seconds}")
            else:
                logger.info(f"Arquivo não encontrado, criando novo: {audio_file.name.value}")
                # Criar novo arquivo
                audio_file_model = AudioFileModel(
                    id=audio_file.file_id.value,
                    owner_id=audio_file.owner_id.value,
                    name=audio_file.name.value,
                    description=audio_file.description.value,
                    path=audio_file.path.value,
                    mime_type=audio_file.file_type.mime_type,
                    extension=audio_file.file_type.extension,
                    category=audio_file.file_type.category.value,
                    size=audio_file.size.value,
                    tags=",".join([tag.value for tag in audio_file.tags]) if audio_file.tags else None,
                    duration_seconds=audio_file.duration_seconds,
                    bitrate=audio_file.bitrate,
                    sample_rate=audio_file.sample_rate,
                    channels=audio_file.channels,
                    genre=audio_file.genre,
                    is_deleted=audio_file.is_deleted,
                    created_at=audio_file.created_at,
                    updated_at=audio_file.updated_at,
                    last_accessed_at=audio_file.last_accessed_at
                )
                self._session.add(audio_file_model)
                logger.info(f"Novo arquivo criado: {audio_file_model.name}")
            
            # Salvar alterações
            await self._session.flush()
            await self._session.commit()
            logger.info(f"Alterações salvas com sucesso para o arquivo: {audio_file.name.value}")
            
        except IntegrityError as e:
            logger.error(f"Erro de integridade ao salvar arquivo: {str(e)}")
            await self._session.rollback()
            raise ValueError(f"Erro ao salvar arquivo: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao salvar arquivo: {str(e)}")
            await self._session.rollback()
            raise ValueError(f"Erro ao salvar arquivo: {str(e)}")
        
    async def find_by_id(self, file_id: FileId) -> Optional[AudioFile]:
        """Busca arquivo por ID."""
        stmt = select(AudioFileModel).where(AudioFileModel.id == file_id.value)
        result = await self._session.execute(stmt)
        audio_file_model = result.scalar_one_or_none()
        
        if audio_file_model:
            return self._model_to_entity(audio_file_model)
        return None

    async def find_by_owner_id(self, owner_id: UserId) -> List[AudioFile]:
        """Busca arquivos por proprietário."""
        stmt = (
            select(AudioFileModel)
            .where(AudioFileModel.owner_id == owner_id.value)
            .where(AudioFileModel.is_deleted == False)
            .order_by(AudioFileModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        audio_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in audio_file_models]

    async def find_by_name_and_owner(self, name: str, owner_id: UserId) -> Optional[AudioFile]:
        """Busca arquivo por nome e proprietário."""
        stmt = (
            select(AudioFileModel)
            .where(AudioFileModel.name == name)
            .where(AudioFileModel.owner_id == owner_id.value)
            .where(AudioFileModel.is_deleted == False)
        )
        result = await self._session.execute(stmt)
        audio_file_model = result.scalar_one_or_none()
        
        if audio_file_model:
            return self._model_to_entity(audio_file_model)
        return None

    async def find_by_tags(self, tags: List[str], owner_id: UserId) -> List[AudioFile]:
        """Busca arquivos por tags."""
        stmt = (
            select(AudioFileModel)
            .where(AudioFileModel.owner_id == owner_id.value)
            .where(AudioFileModel.is_deleted == False)
        )
        
        # Filtrar por tags (busca por substring nas tags)
        for tag in tags:
            stmt = stmt.where(AudioFileModel.tags.contains(tag))
        
        stmt = stmt.order_by(AudioFileModel.created_at.desc())
        result = await self._session.execute(stmt)
        audio_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in audio_file_models]

    async def delete(self, file_id: FileId) -> None:
        """Remove um arquivo (soft delete)."""
        stmt = (
            update(AudioFileModel)
            .where(AudioFileModel.id == file_id.value)
            .values(is_deleted=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def find_all_active(self, limit: int = 100, offset: int = 0) -> List[AudioFile]:
        """Lista arquivos ativos com paginação."""
        stmt = (
            select(AudioFileModel)
            .where(AudioFileModel.is_deleted == False)
            .offset(offset)
            .limit(limit)
            .order_by(AudioFileModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        audio_file_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in audio_file_models]

    def _model_to_entity(self, model: AudioFileModel) -> AudioFile:
        """Converte AudioFileModel para AudioFile entity."""
        from cloud_storage_app.domain.value_objects import (
            FileId, UserId, FileName, FileSize, FilePath, FileType, FileCategory,
            FileDescription, Tag
        )
        
        # Criar instância AudioFile diretamente com os atributos privados
        audio_file = AudioFile.__new__(AudioFile)  # Criar sem chamar __init__
        
        # Definir atributos privados diretamente
        audio_file._file_id = FileId.from_string(model.id)
        audio_file._owner_id = UserId.from_string(model.owner_id)
        audio_file._name = FileName(model.name)
        audio_file._description = FileDescription(model.description)
        audio_file._path = FilePath(model.path)
        audio_file._file_type = FileType(
            mime_type=model.mime_type,
            extension=model.extension,
            category=FileCategory(model.category)
        )
        audio_file._size = FileSize(model.size)
        audio_file._tags = [Tag(tag.strip()) for tag in model.tags.split(",")] if model.tags else []
        audio_file._duration_seconds = model.duration_seconds
        audio_file._bitrate = model.bitrate
        audio_file._sample_rate = model.sample_rate
        audio_file._channels = model.channels
        audio_file._genre = model.genre
        audio_file._is_deleted = model.is_deleted
        audio_file._created_at = model.created_at
        audio_file._updated_at = model.updated_at
        audio_file._last_accessed_at = model.last_accessed_at
        audio_file._domain_events = []
        
        return audio_file