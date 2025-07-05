import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileName:
    """Value object para nome de arquivo"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Nome do arquivo não pode estar vazio")
        
        # Remove espaços extras
        normalized = self.value.strip()
        object.__setattr__(self, 'value', normalized)
        
        if not self.is_valid:
            raise ValueError(f"Nome do arquivo '{self.value}' inválido")
    
    @property
    def is_valid(self) -> bool:
        """Verifica se o nome é válido"""
        if not (1 <= len(self.value) <= 255):
            return False
        
        # Caracteres proibidos no nome do arquivo
        forbidden_chars = r'[<>:"/\\|?*]'
        if re.search(forbidden_chars, self.value):
            return False
        
        # Nomes reservados no Windows
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + \
                        [f'COM{i}' for i in range(1, 10)] + \
                        [f'LPT{i}' for i in range(1, 10)]
        
        name_without_ext = Path(self.value).stem.upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    @property
    def extension(self) -> str:
        """Retorna a extensão do arquivo"""
        return Path(self.value).suffix.lower()
    
    @property
    def name_without_extension(self) -> str:
        """Retorna o nome sem a extensão"""
        return Path(self.value).stem
    
    def __str__(self) -> str:
        return self.value