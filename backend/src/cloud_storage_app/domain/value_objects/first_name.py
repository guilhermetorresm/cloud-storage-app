from dataclasses import dataclass
import re

@dataclass(frozen=True)
class FirstName:
    """Value object para primeiro nome.
    
    Regras de validação:
    - Nome não pode estar vazio
    - Deve ter entre 2 e 50 caracteres
    - Apenas letras, espaços e hífens são permitidos
    - Nome é automaticamente normalizado (capitalizado e espaços removidos)
    """
    value: str

    def __post_init__(self):
        """Normaliza e valida o nome após a inicialização."""
        normalized = self._normalize_name(self.value)
        object.__setattr__(self, 'value', normalized)
        
        if not self.is_valid:
            raise ValueError("Primeiro nome inválido")

    def _normalize_name(self, name: str) -> str:
        """Normaliza um nome removendo espaços extras e capitalizando."""
        return ' '.join(word.capitalize() for word in name.strip().split())

    @property
    def is_valid(self) -> bool:
        """Verifica se o nome é válido de acordo com as regras de negócio."""
        if not self.value:
            return False
        
        # Validação de comprimento
        if not (2 <= len(self.value) <= 50):
            return False
        
        # Validação de caracteres permitidos
        name_pattern = r'^[A-Za-zÀ-ÿ\s-]+$'
        if not re.match(name_pattern, self.value):
            return False
        
        return True

    def __str__(self) -> str:
        return self.value 