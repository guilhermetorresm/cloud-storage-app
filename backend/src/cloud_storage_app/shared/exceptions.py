"""
Exceções customizadas para a aplicação Cloud Storage.
Seguindo a arquitetura Clean, as exceções estão organizadas por domínio.
"""

from typing import Any, Dict, Optional


class CloudStorageException(Exception):
    """Exceção base para toda a aplicação"""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# =============================================================================
# EXCEÇÕES DE DOMÍNIO
# =============================================================================

class DomainException(CloudStorageException):
    """Exceção base para erros de domínio"""
    pass


class ValidationException(DomainException):
    """Exceção para erros de validação de domínio"""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": value}
        )
        self.field = field
        self.value = value


class BusinessRuleException(DomainException):
    """Exceção para violações de regras de negócio"""

    def __init__(self, message: str, rule: str):
        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_VIOLATION",
            details={"rule": rule}
        )
        self.rule = rule


# =============================================================================
# EXCEÇÕES DE USUÁRIO
# =============================================================================

class UserException(DomainException):
    """Exceção base para erros relacionados a usuários"""
    pass


class UserNotFoundException(UserException):
    """Usuário não encontrado"""

    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID '{user_id}' not found",
            error_code="USER_NOT_FOUND",
            details={"user_id": user_id}
        )


class UserAlreadyExistsException(UserException):
    """Usuário já existe"""

    def __init__(self, email: str):
        super().__init__(
            message=f"User with email '{email}' already exists",
            error_code="USER_ALREADY_EXISTS",
            details={"email": email}
        )


class InvalidCredentialsException(UserException):
    """Credenciais inválidas"""

    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            error_code="INVALID_CREDENTIALS"
        )


# =============================================================================
# EXCEÇÕES DE ARQUIVO
# =============================================================================

class FileException(DomainException):
    """Exceção base para erros relacionados a arquivos"""
    pass


class FileNotFoundException(FileException):
    """Arquivo não encontrado"""

    def __init__(self, file_id: str):
        super().__init__(
            message=f"File with ID '{file_id}' not found",
            error_code="FILE_NOT_FOUND",
            details={"file_id": file_id}
        )


class FileAccessDeniedException(FileException):
    """Acesso ao arquivo negado"""

    def __init__(self, file_id: str, user_id: str):
        super().__init__(
            message=f"Access denied to file '{file_id}' for user '{user_id}'",
            error_code="FILE_ACCESS_DENIED",
            details={"file_id": file_id, "user_id": user_id}
        )


class FileTooLargeException(FileException):
    """Arquivo muito grande"""

    def __init__(self, size: int, max_size: int):
        super().__init__(
            message=f"File size ({size} bytes) exceeds maximum allowed ({max_size} bytes)",
            error_code="FILE_TOO_LARGE",
            details={"size": size, "max_size": max_size}
        )


class InvalidFileTypeException(FileException):
    """Tipo de arquivo inválido"""

    def __init__(self, file_type: str, allowed_types: list[str]):
        super().__init__(
            message=f"File type '{file_type}' not allowed. Allowed types: {', '.join(allowed_types)}",
            error_code="INVALID_FILE_TYPE",
            details={"file_type": file_type, "allowed_types": allowed_types}
        )


class FileAlreadyExistsException(FileException):
    """Arquivo já existe"""

    def __init__(self, filename: str, folder_id: Optional[str] = None):
        super().__init__(
            message=f"File '{filename}' already exists in this location",
            error_code="FILE_ALREADY_EXISTS",
            details={"filename": filename, "folder_id": folder_id}
        )


# =============================================================================
# EXCEÇÕES DE AUTENTICAÇÃO E AUTORIZAÇÃO
# =============================================================================

class AuthenticationException(CloudStorageException):
    """Exceção base para erros de autenticação"""
    pass


class TokenExpiredException(AuthenticationException):
    """Token expirado"""

    def __init__(self):
        super().__init__(
            message="Authentication token has expired",
            error_code="TOKEN_EXPIRED"
        )


class InvalidTokenException(AuthenticationException):
    """Token inválido"""

    def __init__(self):
        super().__init__(
            message="Invalid authentication token",
            error_code="INVALID_TOKEN"
        )


class AuthorizationException(CloudStorageException):
    """Exceção base para erros de autorização"""
    pass


class InsufficientPermissionsException(AuthorizationException):
    """Permissões insuficientes"""

    def __init__(self, required_permission: str):
        super().__init__(
            message=f"Insufficient permissions. Required: {required_permission}",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_permission": required_permission}
        )


# =============================================================================
# EXCEÇÕES DE INFRAESTRUTURA
# =============================================================================

class InfrastructureException(CloudStorageException):
    """Exceção base para erros de infraestrutura"""
    pass


class DatabaseException(InfrastructureException):
    """Exceção para erros de banco de dados"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Database error: {message}",
            error_code="DATABASE_ERROR",
            details={"original_error": str(original_error) if original_error else None}
        )


class StorageException(InfrastructureException):
    """Exceção para erros de armazenamento (S3, etc.)"""

    def __init__(self, message: str, operation: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Storage error during {operation}: {message}",
            error_code="STORAGE_ERROR",
            details={
                "operation": operation,
                "original_error": str(original_error) if original_error else None
            }
        )


class ExternalServiceException(InfrastructureException):
    """Exceção para erros de serviços externos"""

    def __init__(self, service: str, message: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "status_code": status_code}
        )