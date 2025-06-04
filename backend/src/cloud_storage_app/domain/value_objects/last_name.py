from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class LastName:
    """Value object para sobrenome.
    
    Regras de validação:
    - Pode ser vazio (None)
    - Se fornecido, deve ter entre 2 e 100 caracteres
    - Apenas letras, espaços e hífens são permitidos
    - Nome é automaticamente normalizado (capitalizado e espaços removidos)
    """
    value: Optional[str] = None

    def __post_init__(self):
        """Normaliza e valida o sobrenome após a inicialização."""
        if self.value:
            normalized = self._normalize_name(self.value)
            object.__setattr__(self, 'value', normalized)
            
            if not self.is_valid:
                raise ValueError("Sobrenome inválido")

    def _normalize_name(self, name: str) -> str:
        """Normaliza um nome removendo espaços extras e capitalizando."""
        return ' '.join(word.capitalize() for word in name.strip().split())

    @property
    def is_valid(self) -> bool:
        """Verifica se o sobrenome é válido de acordo com as regras de negócio."""
        if not self.value:
            return True  # Sobrenome é opcional
        
        # Validação de comprimento
        if not (2 <= len(self.value) <= 100):
            return False
        
        # Validação de caracteres permitidos
        name_pattern = r'^[A-Za-zÀ-ÿ\s-]+$'
        if not re.match(name_pattern, self.value):
            return False
        
        return True

    def __str__(self) -> str:
        return self.value or "" 