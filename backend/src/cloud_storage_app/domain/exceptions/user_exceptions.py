"""
Exceções do domínio de usuário.
Estas exceções representam erros específicos relacionados a usuários.
"""

from typing import Optional, Any, Dict


class UserDomainException(Exception):
    """Exceção base para erros do domínio de usuário."""
    
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


class UserAlreadyExistsException(UserDomainException):
    """Exceção lançada quando tenta criar um usuário que já existe."""
    
    def __init__(self, identifier: str, identifier_type: str = "email"):
        """
        Args:
            identifier: O identificador que causou o conflito (email ou username)
            identifier_type: O tipo do identificador ("email" ou "username")
        """
        super().__init__(
            message=f"User with this {identifier_type} already exists",
            error_code="USER_ALREADY_EXISTS",
            details={
                "identifier": identifier,
                "identifier_type": identifier_type
            }
        )


class UserNotFoundException(UserDomainException):
    """Exceção lançada quando um usuário não é encontrado."""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID '{user_id}' not found",
            error_code="USER_NOT_FOUND",
            details={"user_id": user_id}
        )


class InvalidUserCredentialsException(UserDomainException):
    """Exceção lançada quando as credenciais do usuário são inválidas."""
    
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(
            message=message,
            error_code="INVALID_CREDENTIALS"
        )


class UserValidationException(UserDomainException):
    """Exceção lançada quando há erro de validação nos dados do usuário."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None
    ):
        super().__init__(
            message=message,
            error_code="USER_VALIDATION_ERROR",
            details={
                "field": field,
                "value": value
            }
        )


class UserInactiveException(UserDomainException):
    """Exceção lançada quando tenta acessar um usuário inativo."""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID '{user_id}' is inactive",
            error_code="USER_INACTIVE",
            details={"user_id": user_id}
        )


class UserPasswordException(UserDomainException):
    """Exceção base para erros relacionados a senha do usuário."""
    pass


class InvalidPasswordException(UserPasswordException):
    """Exceção lançada quando a senha não atende aos requisitos."""
    
    def __init__(self, message: str = "Password does not meet requirements"):
        super().__init__(
            message=message,
            error_code="INVALID_PASSWORD"
        )


class PasswordMismatchException(UserPasswordException):
    """Exceção lançada quando as senhas não coincidem."""
    
    def __init__(self):
        super().__init__(
            message="Passwords do not match",
            error_code="PASSWORD_MISMATCH"
        ) 