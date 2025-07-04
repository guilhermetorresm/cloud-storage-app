from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Tag:
    """Value object para nome de tag.
    
    Regras de validação:
    - Nome não pode estar vazio
    - Deve ter entre 1 e 50 caracteres
    - Apenas letras, espaços e hífens são permitidos
    """
    value: str

    def __post_init__(self):
        """Valida o nome após a inicialização."""
        if not self.is_valid:
            raise ValueError("Nome de tag inválido")

    @property
    def is_valid(self) -> bool:
        """Verifica se o nome é válido de acordo com as regras de negócio."""
        if not self.value:
            return False
        
        # Validação de comprimento
        if not (1 <= len(self.value) <= 50):
            return False
        
        # Validação de caracteres permitidos
        name_pattern = r'^[A-Za-zÀ-ÿ\s-]+$'
        if not re.match(name_pattern, self.value):
            return False
        
        return True

    def __str__(self) -> str:
        return self.value 