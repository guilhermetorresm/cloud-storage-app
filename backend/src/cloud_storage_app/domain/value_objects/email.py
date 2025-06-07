import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Value object para endereços de e-mail"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Endereço de e-mail '{self.value}' inválido")
        
    @staticmethod
    def _is_valid_email(value: str) -> bool:
        """Verifica se o endereço de e-mail é válido"""
        return re.match(r"[^@]+@[^@]+\.[^@]+", value) is not None
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def local_part(self) -> str:
        """Parte local do endereço de e-mail"""
        return self.value.split("@")[0]
    
    @property
    def domain(self) -> str:
        """Domínio do endereço de e-mail"""
        return self.value.split("@")[1]
