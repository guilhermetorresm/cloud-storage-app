from uuid import UUID, uuid4
from typing import Union
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """Value object para IDs de usuários"""
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise ValueError("ID de usuário deve ser um UUID válido")

    @classmethod
    def generate(cls) -> "UserId":
        """Gera um novo user ID"""
        return cls(value=uuid4())
    
    @classmethod
    def from_string(cls, value: Union[str, UUID]) -> "UserId":
        if isinstance(value, str):
            try:
                value = UUID(value)
            except ValueError:
                raise ValueError(f"String '{value}' não é um UUID válido")
        return cls(value=value)
    
    def __str__(self) -> str:
        return str(self.value)
