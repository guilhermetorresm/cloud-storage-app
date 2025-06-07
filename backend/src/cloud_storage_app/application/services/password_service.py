from cloud_storage_app.domain.services.password_service import IPasswordService
from cloud_storage_app.domain.value_objects import Password, HashedPassword
from typing import Tuple


class PasswordApplicationService:
    """Application service for password operations."""
    
    def __init__(self, password_service: IPasswordService):
        self._password_service = password_service
    
    def create_password_hash(self, plain_password: str) -> str:
        """
        Create a password hash from a plain text password.
        
        Args:
            plain_password: The plain text password
            
        Returns:
            str: The hashed password
            
        Raises:
            ValueError: If password is invalid
        """
        password = Password(value=plain_password)
        hashed_password = self._password_service.hash_password(password)
        return hashed_password.value
    
    def verify_password_match(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if a plain text password matches a hashed password.
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password to compare against
            
        Returns:
            bool: True if passwords match, False otherwise
        """
        try:
            password = Password(value=plain_password)
            hashed = HashedPassword(value=hashed_password)
            return self._password_service.verify_password(password, hashed)
        except ValueError:
            return False
    
    def validate_password_strength(self, plain_password: str) -> Tuple[bool, list[str]]:
        """
        Validate password strength and return validation errors.
        
        Args:
            plain_password: The plain text password to validate
            
        Returns:
            Tuple[bool, list[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            password = Password(value=plain_password)
            is_strong = self._password_service.is_password_strong(password)
            return is_strong, errors
        except ValueError as e:
            errors.append(str(e))
            return False, errors
    
    def should_rehash_password(self, hashed_password: str) -> bool:
        """
        Check if a password should be rehashed due to updated security parameters.
        
        Args:
            hashed_password: The hashed password to check
            
        Returns:
            bool: True if password should be rehashed
        """
        try:
            hashed = HashedPassword(value=hashed_password)
            if hasattr(self._password_service, 'needs_rehash'):
                return self._password_service.needs_rehash(hashed)
            return False
        except ValueError:
            return False
