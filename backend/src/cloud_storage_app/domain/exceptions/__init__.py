"""
Exceções do domínio.
"""

from .user_exceptions import (
    UserDomainException,
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidUserCredentialsException,
    UserValidationException,
    UserInactiveException,
    UserPasswordException,
    InvalidPasswordException,
    PasswordMismatchException
)

from .file_exceptions import (
    FileDomainException,
    FileNotFoundException,
    FileValidationException,
    FileUploadException,
    FileTypeNotSupportedException,
    FileSizeExceededException,
    FileAccessDeniedException,
    FileAlreadyExistsException
)

__all__ = [
    # User exceptions
    "UserDomainException",
    "UserAlreadyExistsException", 
    "UserNotFoundException",
    "InvalidUserCredentialsException",
    "UserValidationException",
    "UserInactiveException",
    "UserPasswordException",
    "InvalidPasswordException",
    "PasswordMismatchException",
    
    # File exceptions
    "FileDomainException",
    "FileNotFoundException",
    "FileValidationException",
    "FileUploadException",
    "FileTypeNotSupportedException",
    "FileSizeExceededException",
    "FileAccessDeniedException",
    "FileAlreadyExistsException"
] 