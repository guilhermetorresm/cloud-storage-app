"""
Manipuladores de exceção para a API FastAPI.
Converte exceções em respostas HTTP apropriadas.
"""

import logging
from typing import Any, Dict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from ...shared.exceptions import (
    CloudStorageException,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
    BusinessRuleException,
    UserNotFoundException,
    FileNotFoundException,
    FileAccessDeniedException,
    FileTooLargeException,
    InvalidFileTypeException,
    DatabaseException,
    StorageException,
)

logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> JSONResponse:
    """Cria uma resposta de erro padronizada"""
    
    response_data = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    
    if details:
        response_data["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Manipula exceções HTTP padrão do FastAPI"""
    
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return create_error_response(
        error_code="HTTP_ERROR",
        message=exc.detail,
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Manipula erros de validação do Pydantic"""
    
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Formatar erros de validação
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Invalid request data",
        details={"validation_errors": formatted_errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manipula todas as outras exceções"""
    
    if isinstance(exc, CloudStorageException):
        return await cloud_storage_exception_handler(request, exc)
    
    # Exceção não tratada - log completo para debug
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    return create_error_response(
        error_code="INTERNAL_ERROR",
        message="An internal error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


async def cloud_storage_exception_handler(request: Request, exc: CloudStorageException) -> JSONResponse:
    """Manipula exceções específicas da aplicação Cloud Storage"""
    
    # Mapeamento de exceções para códigos HTTP
    status_mapping = {
        # Autenticação e Autorização
        AuthenticationException: status.HTTP_401_UNAUTHORIZED,
        AuthorizationException: status.HTTP_403_FORBIDDEN,
        
        # Validação e Regras de Negócio
        ValidationException: status.HTTP_400_BAD_REQUEST,
        BusinessRuleException: status.HTTP_400_BAD_REQUEST,
        
        # Não encontrado
        UserNotFoundException: status.HTTP_404_NOT_FOUND,
        FileNotFoundException: status.HTTP_404_NOT_FOUND,
        
        # Acesso negado
        FileAccessDeniedException: status.HTTP_403_FORBIDDEN,
        
        # Arquivos
        FileTooLargeException: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        InvalidFileTypeException: status.HTTP_400_BAD_REQUEST,
        
        # Infraestrutura
        DatabaseException: status.HTTP_503_SERVICE_UNAVAILABLE,
        StorageException: status.HTTP_503_SERVICE_UNAVAILABLE,
    }
    
    # Determinar código de status HTTP
    http_status = status.HTTP_400_BAD_REQUEST  # default
    for exception_type, status_code in status_mapping.items():
        if isinstance(exc, exception_type):
            http_status = status_code
            break
    
    # Log da exceção
    if http_status >= 500:
        logger.error(f"Server error: {exc.error_code} - {exc.message}", exc_info=True)
    else:
        logger.warning(f"Client error: {exc.error_code} - {exc.message}")
    
    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details if exc.details else None,
        status_code=http_status
    )