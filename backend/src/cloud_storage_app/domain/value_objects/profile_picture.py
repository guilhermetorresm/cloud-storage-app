from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class ProfilePicture:
    """Value object para imagens de perfil"""
    value: Optional[str] = None

    def __post_init__(self):
        if self.value and not self._is_valid_url(self.value):
            raise ValueError("URL de imagem de perfil inválida")
        
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Verifica se a URL é válida"""
        if not url:
            return False
        if not re.match(r"^https?://", url):
            return False
        return True
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def has_picture(self) -> bool:
        """Verifica se o usuário tem uma imagem de perfil"""
        return bool(self.value)
