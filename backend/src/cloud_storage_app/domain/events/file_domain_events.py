from dataclasses import dataclass
from datetime import datetime
from .domain_event import DomainEvent
from ..value_objects import FileId, UserId, FileName, FileType


@dataclass
class FileCreated(DomainEvent):
    """Evento disparado quando um arquivo é criado"""
    file_id: FileId = None
    owner_id: UserId = None
    file_name: FileName = None
    file_type: FileType = None
    occurred_at: datetime = None
    
    @property
    def event_type(self) -> str:
        return "file.created"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)


@dataclass
class FileUpdated(DomainEvent):
    """Evento disparado quando um arquivo é atualizado"""
    file_id: FileId = None
    owner_id: UserId = None
    change_description: str = None
    occurred_at: datetime = None
    
    @property
    def event_type(self) -> str:
        return "file.updated"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)


@dataclass
class FileDeleted(DomainEvent):
    """Evento disparado quando um arquivo é deletado"""
    file_id: FileId = None
    owner_id: UserId = None
    occurred_at: datetime = None
    
    @property
    def event_type(self) -> str:
        return "file.deleted"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)


@dataclass
class FileAccessed(DomainEvent):
    """Evento disparado quando um arquivo é acessado"""
    file_id: FileId = None
    owner_id: UserId = None
    access_type: str = None  # 'download', 'view', 'stream', etc.
    occurred_at: datetime = None
    
    @property
    def event_type(self) -> str:
        return "file.accessed"
    
    @property
    def aggregate_id(self) -> str:
        return str(self.file_id)