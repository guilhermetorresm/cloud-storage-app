from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional, List
from ..value_objects import (
    FileId, FileName, FileSize, FilePath, FileType, UserId, FileDescription, Tag
)
from ..events.domain_event import DomainEvent
from ..events.file_domain_events import FileCreated, FileDeleted, FileUpdated


@dataclass
class BaseFile(ABC):
    """
    Classe abstrata base para todas as entidades de arquivo.
    
    Representa o comportamento comum a todos os tipos de arquivo
    no sistema de cloud storage.
    """
    
    # Identificadores
    _file_id: FileId
    _owner_id: UserId
    _name: FileName
    _description: FileDescription
    _path: FilePath
    _file_type: FileType
    
    _tags: List[Tag]

    # Metadados básicos
    _size: FileSize
    
    # Controle de estado
    _is_deleted: bool = False
    
    # Timestamps
    _created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _last_accessed_at: Optional[datetime] = None
    
    # Eventos de domínio
    _domain_events: List[DomainEvent] = field(default_factory=list)
    
    def __post_init__(self):
        """Validações básicas após inicialização"""
        if not self._file_id:
            raise ValueError("ID do arquivo é obrigatório")
        if not self._owner_id:
            raise ValueError("ID do proprietário é obrigatório")
        if not self._name:
            raise ValueError("Nome do arquivo é obrigatório")
        if not self._path:
            raise ValueError("Caminho do arquivo é obrigatório")
    
    @classmethod
    def create(cls, owner_id: UserId, name: str, path: str, 
               size: int, description: str, tags: List[Tag], **kwargs) -> "BaseFile":
        """
        Cria uma nova instância de arquivo.
        
        Args:
            owner_id: ID do proprietário
            name: Nome do arquivo
            path: Caminho do arquivo
            size: Tamanho em bytes
            description: Descrição do arquivo
            tags: Lista de tags
            **kwargs: Argumentos específicos do tipo de arquivo
        """
        file_name = FileName(name)
        file_type = FileType.from_extension(file_name.extension)
        
        file_instance = cls(
            _file_id=FileId.generate(),
            _owner_id=owner_id,
            _name=file_name,
            _path=FilePath(path),
            _file_type=file_type,
            _size=FileSize(size),
            _description=FileDescription(description),
            _tags=tags,
            **kwargs
        )
        
        file_instance._add_domain_event(
            FileCreated(file_instance.file_id, file_instance.owner_id, 
                       file_instance.name, file_instance.file_type, 
                       file_instance.created_at)
        )
        
        return file_instance
    
    # Getters
    @property
    def file_id(self) -> FileId:
        return self._file_id
    
    @property
    def owner_id(self) -> UserId:
        return self._owner_id
    
    @property
    def name(self) -> FileName:
        return self._name
    
    @property
    def path(self) -> FilePath:
        return self._path
    
    @property
    def description(self) -> FileDescription:
        return self._description
    
    @property
    def file_type(self) -> FileType:
        return self._file_type
    
    @property
    def size(self) -> FileSize:
        return self._size
    
    @property
    def tags(self) -> List[Tag]:
        return self._tags
    
    @property
    def is_deleted(self) -> bool:
        return self._is_deleted
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def last_accessed_at(self) -> Optional[datetime]:
        return self._last_accessed_at
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def add_tag(self, tag: Tag) -> None:
        """Adiciona uma tag ao arquivo"""
        if tag in self._tags:
            raise ValueError("Tag já existe no arquivo")
        self._tags.append(tag)
        self._mark_as_updated()
    
    def remove_tag(self, tag: Tag) -> None:
        """Remove uma tag do arquivo"""
        if tag not in self._tags:
            raise ValueError("Tag não existe no arquivo")
        self._tags.remove(tag)
        self._mark_as_updated()

    def clear_tags(self) -> None:
        """Limpa todas as tags do arquivo"""
        self._tags.clear()
        self._mark_as_updated()
    
    def update_tags(self, tags: List[Tag]) -> None:
        """Atualiza as tags do arquivo"""
        self._tags = tags
        self._mark_as_updated()
    
    # Métodos de domínio
    def rename(self, new_name: str) -> None:
        """Renomeia o arquivo"""
        if self._is_deleted:
            raise ValueError("Não é possível renomear um arquivo deletado")
        
        old_name = self._name
        self._name = FileName(new_name)
        self._mark_as_updated()
        
        self._add_domain_event(
            FileUpdated(self._file_id, self._owner_id, 
                       f"Arquivo renomeado de '{old_name}' para '{new_name}'",
                       self._updated_at)
        )
    
    def update_description(self, new_description: str) -> None:
        """Atualiza a descrição do arquivo"""
        self._description = FileDescription(new_description)
        self._mark_as_updated()
    
    def move(self, new_path: str) -> None:
        """Move o arquivo para um novo caminho"""
        if self._is_deleted:
            raise ValueError("Não é possível mover um arquivo deletado")
        
        old_path = self._path
        self._path = FilePath(new_path)
        self._mark_as_updated()
        
        self._add_domain_event(
            FileUpdated(self._file_id, self._owner_id,
                       f"Arquivo movido de '{old_path}' para '{new_path}'",
                       self._updated_at)
        )
    
    def delete(self) -> None:
        """Marca o arquivo como deletado (soft delete)"""
        if self._is_deleted:
            raise ValueError("Arquivo já está deletado")
        
        self._is_deleted = True
        self._mark_as_updated()
        
        self._add_domain_event(
            FileDeleted(self._file_id, self._owner_id, self._updated_at)
        )
    
    def restore(self) -> None:
        """Restaura um arquivo deletado"""
        if not self._is_deleted:
            raise ValueError("Arquivo não está deletado")
        
        self._is_deleted = False
        self._mark_as_updated()
        
        self._add_domain_event(
            FileUpdated(self._file_id, self._owner_id,
                       "Arquivo restaurado", self._updated_at)
        )
    
    def update_last_accessed(self) -> None:
        """Atualiza o timestamp do último acesso"""
        self._last_accessed_at = datetime.now(UTC)
    
    def _mark_as_updated(self) -> None:
        """Marca o arquivo como atualizado"""
        self._updated_at = datetime.now(UTC)
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Adiciona um evento de domínio"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Limpa os eventos de domínio"""
        self._domain_events.clear()
    
    @abstractmethod
    def get_metadata(self) -> dict:
        """Retorna metadados específicos do tipo de arquivo"""
        pass
    
    @abstractmethod
    def is_valid_file_type(self) -> bool:
        """Verifica se o tipo de arquivo é válido para esta entidade"""
        pass