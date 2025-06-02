from dataclasses import dataclass
import re
from typing import List

@dataclass(frozen=True)
class Password:
    """Value object para senhas.
    
    Regras de validação:
    - Mínimo de 8 caracteres
    - Máximo de 128 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    - Não pode conter espaços
    - Não pode conter caracteres Unicode
    """
    value: str

    def __post_init__(self):
        """Valida a senha de acordo com as regras de negócio."""
        errors = self._validate_password()
        if errors:
            raise ValueError("\n".join(errors))

    def _validate_password(self) -> List[str]:
        """Realiza todas as validações da senha e retorna lista de erros."""
        errors = []
        
        # Validação básica
        if not self.value:
            return ["Senha não pode ser vazia"]
        
        # Validação de comprimento
        if len(self.value) < 8:
            errors.append("Senha deve ter pelo menos 8 caracteres")
        if len(self.value) > 128:
            errors.append("Senha não pode ter mais de 128 caracteres")
        
        # Validação de caracteres
        if not re.search(r"[A-Z]", self.value):
            errors.append("Senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", self.value):
            errors.append("Senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"[0-9]", self.value):
            errors.append("Senha deve conter pelo menos um número")
        if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]", self.value):
            errors.append("Senha deve conter pelo menos um caractere especial")
        
        # Validações adicionais de segurança
        if re.search(r"\s", self.value):
            errors.append("Senha não pode conter espaços")
        if not self.value.isascii():
            errors.append("Senha não pode conter caracteres especiais Unicode")
        
        
        return errors

    def __str__(self) -> str:
        return self.value
