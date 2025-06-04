from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserDescription:
    """Value object para descrições de usuários"""
    value: Optional[str] = None

    def __post_init__(self):
        if self.value and len(self.value) > 500:
            raise ValueError("Descrição de usuário muito longa")
        
    def __str__(self) -> str:
        return self.value or ""
    
    @property
    def is_empty(self) -> bool:
        """Verifica se a descrição está vazia"""
        return not self.value or not self.value.strip()
    