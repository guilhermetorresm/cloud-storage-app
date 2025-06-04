from abc import ABC, abstractmethod
from domain.value_objects import Password, HashedPassword


class IPasswordService(ABC):
    """Interface for password service operations."""
    
    @abstractmethod
    def hash_password(self, password: Password) -> HashedPassword:
        """Hash a plain text password."""
        pass
    
    @abstractmethod
    def verify_password(self, password: Password, hashed_password: HashedPassword) -> bool:
        """Verify a plain text password against a hashed password."""
        pass
    
    @abstractmethod
    def is_password_strong(self, password: Password) -> bool:
        """Check if password meets strength requirements."""
        pass