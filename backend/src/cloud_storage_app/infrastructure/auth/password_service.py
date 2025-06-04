from passlib.context import CryptContext
from domain.services.password_service import IPasswordService
from domain.value_objects import Password, HashedPassword
import logging

logger = logging.getLogger(__name__)


class PasswordService(IPasswordService):
    """Concrete implementation of password service using bcrypt."""
    
    def __init__(self):
        self._pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12  # Higher rounds for better security
        )
    
    def hash_password(self, password: Password) -> HashedPassword:
        """
        Hash a plain text password using bcrypt.
        
        Args:
            password: Password value object containing the plain text password
            
        Returns:
            HashedPassword value object containing the hashed password
            
        Raises:
            ValueError: If password is invalid or hashing fails
        """
        try:
            hashed = self._pwd_context.hash(password.value)
            return HashedPassword(value=hashed)
        except Exception as e:
            logger.error(f"Failed to hash password: {str(e)}")
            raise ValueError("Failed to hash password") from e
    
    def verify_password(self, password: Password, hashed_password: HashedPassword) -> bool:
        """
        Verify a plain text password against a hashed password.
        
        Args:
            password: Password value object containing the plain text password
            hashed_password: HashedPassword value object containing the hashed password
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return self._pwd_context.verify(password.value, hashed_password.value)
        except Exception as e:
            logger.error(f"Failed to verify password: {str(e)}")
            return False
    
    def is_password_strong(self, password: Password) -> bool:
        """
        Check if password meets strength requirements.
        
        Args:
            password: Password value object to check
            
        Returns:
            bool: True if password is strong, False otherwise
        """
        try:
            # The Password value object constructor already validates strength
            # If we reach here, the password is valid
            return True
        except ValueError:
            return False
    
    def needs_rehash(self, hashed_password: HashedPassword) -> bool:
        """
        Check if a hashed password needs to be rehashed (e.g., due to updated security parameters).
        
        Args:
            hashed_password: HashedPassword value object to check
            
        Returns:
            bool: True if password needs rehashing, False otherwise
        """
        try:
            return self._pwd_context.needs_update(hashed_password.value)
        except Exception as e:
            logger.error(f"Failed to check if password needs rehash: {str(e)}")
            return False
