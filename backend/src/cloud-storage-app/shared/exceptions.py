# src/cloud_storage/shared/exceptions.py
from typing import Optional, Dict, Any


class CloudStorageException(Exception):
    """Exceção base para todas as exceções do sistema"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DomainException(CloudStorageException):
    """Exceção base para violações de regras de domínio"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ValidationException(DomainException):
    """Exceção para erros de validação de dados"""
    
    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(f"Validation error in field '{field}': {message}")
        self.field = field
        self.value = value
        self.details = {"field": field, "value": value}


class BusinessRuleException(DomainException):
    """Exceção para violações de regras de negócio"""
    pass


class EntityNotFoundException(DomainException):
    """Exceção quando uma entidade não é encontrada"""
    
    def __init__(self, entity_type: str, identifier: str):
        message = f"{entity_type} with identifier '{identifier}' not found"
        super().__init__(message)
        self.entity_type = entity_type
        self.identifier = identifier
        self.details = {"entity_type": entity_type, "identifier": identifier}


class EntityAlreadyExistsException(DomainException):
    """Exceção quando uma entidade já existe"""
    
    def __init__(self, entity_type: str, identifier: str):
        message = f"{entity_type} with identifier '{identifier}' already exists"
        super().__init__(message)
        self.entity_type = entity_type
        self.identifier = identifier
        self.details = {"entity_type": entity_type, "identifier": identifier}


class InfrastructureException(CloudStorageException):
    """Exceção base para problemas de infraestrutura"""
    pass


class DatabaseException(InfrastructureException):
    """Exceção para problemas relacionados ao banco de dados"""
    pass


class StorageException(InfrastructureException):
    """Exceção para problemas relacionados ao armazenamento"""
    pass


class AuthenticationException(CloudStorageException):
    """Exceção para problemas de autenticação"""
    pass


class AuthorizationException(CloudStorageException):
    """Exceção para problemas de autorização"""
    pass