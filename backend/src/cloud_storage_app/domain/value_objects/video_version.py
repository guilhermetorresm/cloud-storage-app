from dataclasses import dataclass
from typing import Optional
from .file_path import FilePath


@dataclass(frozen=True)
class VideoVersion:
    """
    Objeto de Valor que representa uma versão específica de um vídeo.
    
    Cada versão tem uma resolução específica e um caminho único no S3.
    """
    resolution: str  # ex: "480p", "720p", "1080p", "4K"
    file_path: FilePath
    is_original: bool = False  # Indica se é a versão original do usuário
    processing_status: str = "pending"  # pending, processing, completed, failed
    
    def __post_init__(self):
        """Validações básicas"""
        if not self.resolution:
            raise ValueError("Resolução não pode ser vazia")
        if not self.file_path:
            raise ValueError("Caminho do arquivo não pode ser vazio")
        if self.processing_status not in ["pending", "processing", "completed", "failed"]:
            raise ValueError("Status de processamento inválido")
    
    @property
    def height(self) -> Optional[int]:
        """Extrai a altura da resolução (ex: '1080p' -> 1080)"""
        if not self.resolution:
            return None
        
        # Remove 'p' ou 'K' e converte para int
        resolution_str = self.resolution.lower()
        if resolution_str.endswith('p'):
            try:
                return int(resolution_str[:-1])
            except ValueError:
                return None
        elif resolution_str == '4k':
            return 2160
        elif resolution_str == '2k':
            return 1440
        else:
            return None
    
    @property
    def is_ready(self) -> bool:
        """Verifica se a versão está pronta para uso"""
        return self.processing_status == "completed"
    
    @property
    def is_processing(self) -> bool:
        """Verifica se a versão está sendo processada"""
        return self.processing_status == "processing"
    
    @property
    def has_failed(self) -> bool:
        """Verifica se o processamento da versão falhou"""
        return self.processing_status == "failed"
    
    def __str__(self) -> str:
        return f"VideoVersion(resolution={self.resolution}, status={self.processing_status}, original={self.is_original})" 