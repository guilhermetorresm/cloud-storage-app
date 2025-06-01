from dataclasses import dataclass

@dataclass(frozen=True)
class HashedPassword:
    """Value object para senhas hasheadas"""
    value: str

    def __post_init__(self):
        if not self._is_valid_hash(self.value):
            raise ValueError("Hash de senha inválido")
        
    @staticmethod
    def _is_valid_hash(self, hash: str) -> bool:
        """Verifica se o hash é válido"""
        if self.value is None:
            return False
        if len(self.value) < 60:
            return False
        return True
    
    def __str__(self) -> str:
        return self.value
    
    def verify(self, plain_password: str, hash_function) -> bool:
        """Verifica se a senha corresponde ao hash"""
        return hash_function(plain_password, self.value)
