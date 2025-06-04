import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Username:
    """Value object para nomes de usuários"""
    value: str

    def __post_init__(self):
        if not self._is_valid_username(self.value):
            raise ValueError(f"Nome de usuário '{self.value}' inválido")
        
    @staticmethod
    def _is_valid_username(username: str) -> bool:
        """Verifica se o nome de usuário é válido"""
        if not username:
            return False
        if len(username) < 3 or len(username) > 30:
            return False
        # Apenas letras, números, underscores e hífens
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            return False
        return True
    
    def __str__(self) -> str:
        return self.value
