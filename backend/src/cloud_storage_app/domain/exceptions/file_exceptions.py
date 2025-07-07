"""
Exceções do domínio de arquivos.
Estas exceções representam erros específicos relacionados a arquivos.
"""

from typing import Optional, Any, Dict


class FileDomainException(Exception):
    """Exceção base para erros do domínio de arquivos."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class FileNotFoundException(FileDomainException):
    """Exceção lançada quando um arquivo não é encontrado."""
    
    def __init__(self, file_id: str):
        super().__init__(
            message=f"File with ID '{file_id}' not found",
            error_code="FILE_NOT_FOUND",
            details={"file_id": file_id}
        )


class FileValidationException(FileDomainException):
    """Exceção lançada quando há erro de validação nos dados do arquivo."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None
    ):
        super().__init__(
            message=message,
            error_code="FILE_VALIDATION_ERROR",
            details={
                "field": field,
                "value": value
            }
        )


class FileUploadException(FileDomainException):
    """Exceção lançada quando há erro no upload de arquivo."""
    
    def __init__(self, message: str, file_name: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="FILE_UPLOAD_ERROR",
            details={"file_name": file_name}
        )


class FileTypeNotSupportedException(FileDomainException):
    """Exceção lançada quando o tipo de arquivo não é suportado."""
    
    def __init__(self, file_type: str, supported_types: Optional[list] = None):
        super().__init__(
            message=f"File type '{file_type}' is not supported",
            error_code="FILE_TYPE_NOT_SUPPORTED",
            details={
                "file_type": file_type,
                "supported_types": supported_types
            }
        )


class FileSizeExceededException(FileDomainException):
    """Exceção lançada quando o tamanho do arquivo excede o limite."""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"File size {file_size} exceeds maximum allowed size {max_size}",
            error_code="FILE_SIZE_EXCEEDED",
            details={
                "file_size": file_size,
                "max_size": max_size
            }
        )


class FileAccessDeniedException(FileDomainException):
    """Exceção lançada quando o acesso ao arquivo é negado."""
    
    def __init__(self, file_id: str, user_id: str):
        super().__init__(
            message=f"Access denied to file '{file_id}' for user '{user_id}'",
            error_code="FILE_ACCESS_DENIED",
            details={
                "file_id": file_id,
                "user_id": user_id
            }
        )


class FileAlreadyExistsException(FileDomainException):
    """Exceção lançada quando tenta criar um arquivo que já existe."""
    
    def __init__(self, file_name: str, path: str):
        super().__init__(
            message=f"File '{file_name}' already exists at path '{path}'",
            error_code="FILE_ALREADY_EXISTS",
            details={
                "file_name": file_name,
                "path": path
            }
        ) 