from dataclasses import dataclass

@dataclass(frozen=True)
class HashedPassword:
    """Value object para senhas hasheadas"""
    value: str

    def __post_init__(self):
        if not self.self.value:
            raise ValueError("Hash de senha não pode ser vazio")
