from dataclasses import dataclass
from datetime import datetime
from .domain_event import DomainEvent
from ..value_objects import FileId, UserId, FileName, FileType


@dataclass(frozen=True)
class FileCreated(DomainEvent):
    """Evento disparado quando um arquivo é criado"""
    file_id: FileId
    owner_id: UserId
    file_name: FileName
    file_type: FileType
    occurred_at: datetime
    
    @property
    def event_type(self) -> str:
        return "file.created"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)


@dataclass(frozen=True)
class FileUpdated(DomainEvent):
    """Evento disparado quando um arquivo é atualizado"""
    file_id: FileId
    owner_id: UserId
    change_description: str
    occurred_at: datetime
    
    @property
    def event_type(self) -> str:
        return "file.updated"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)


@dataclass(frozen=True)
class FileDeleted(DomainEvent):
    """Evento disparado quando um arquivo é deletado"""
    file_id: FileId
    owner_id: UserId
    occurred_at: datetime
    
    @property
    def event_type(self) -> str:
        return "file.deleted"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)


@dataclass(frozen=True)
class FileAccessed(DomainEvent):
    """Evento disparado quando um arquivo é acessado"""
    file_id: FileId
    owner_id: UserId
    access_type: str  # 'download', 'view', 'stream', etc.
    occurred_at: datetime
    
    @property
    def event_type(self) -> str:
        return "file.accessed"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)