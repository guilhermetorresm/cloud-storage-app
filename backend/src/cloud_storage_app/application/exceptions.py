"""
Exceções específicas da camada de aplicação.
Define exceções de alto nível para casos de uso.
"""

from typing import Optional, Dict, Any


class ApplicationException(Exception):
    """Exceção base para a camada de aplicação"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationException(ApplicationException):
    """Exceção para erros de autenticação"""
    pass


class InvalidCredentialsException(AuthenticationException):
    """Exceção para credenciais inválidas"""
    pass


class UserNotFoundException(ApplicationException):
    """Exceção para usuário não encontrado"""
    pass


class UserAlreadyExistsException(ApplicationException):
    """Exceção para usuário já existente"""
    pass


class ValidationException(ApplicationException):
    """Exceção para erros de validação"""
    pass


class AuthorizationException(ApplicationException):
    """Exceção para erros de autorização"""
    pass


class TokenException(ApplicationException):
    """Exceção para erros relacionados a tokens"""
    pass


class ExpiredTokenException(TokenException):
    """Exceção para tokens expirados"""
    pass


class InvalidTokenException(TokenException):
    """Exceção para tokens inválidos"""
    pass