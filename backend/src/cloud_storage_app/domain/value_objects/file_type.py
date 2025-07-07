from dataclasses import dataclass
from enum import Enum
from typing import Set


class FileCategory(Enum):
    """Categoria de arquivo."""
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"


@dataclass(frozen=True)
class FileType:
    """Value Object para tipo de arquivo."""
    
    mime_type: str
    extension: str
    category: FileCategory
    
    # Tipos de arquivo suportados
    SUPPORTED_TYPES = {
        # Áudio
        'audio/mp3': ('mp3', FileCategory.AUDIO),
        'audio/mpeg': ('mp3', FileCategory.AUDIO),
        'audio/wav': ('wav', FileCategory.AUDIO),
        'audio/ogg': ('ogg', FileCategory.AUDIO),
        'audio/flac': ('flac', FileCategory.AUDIO),
        
        # Imagem
        'image/jpeg': ('jpg', FileCategory.IMAGE),
        'image/jpg': ('jpg', FileCategory.IMAGE),
        'image/png': ('png', FileCategory.IMAGE),
        'image/gif': ('gif', FileCategory.IMAGE),
        'image/webp': ('webp', FileCategory.IMAGE),
        'image/svg+xml': ('svg', FileCategory.IMAGE),
        
        # Vídeo
        'video/mp4': ('mp4', FileCategory.VIDEO),
        'video/avi': ('avi', FileCategory.VIDEO),
        'video/mov': ('mov', FileCategory.VIDEO),
        'video/webm': ('webm', FileCategory.VIDEO),
    }
    
    def __post_init__(self):
        if not self.mime_type:
            raise ValueError("Tipo MIME não pode ser vazio")
        
        if not self.extension:
            raise ValueError("Extensão não pode ser vazia")
        
        if self.mime_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Tipo de arquivo não suportado: {self.mime_type}")
    
    @classmethod
    def from_mime_type(cls, mime_type: str) -> "FileType":
        """Cria um FileType a partir do tipo MIME."""
        if mime_type not in cls.SUPPORTED_TYPES:
            raise ValueError(f"Tipo de arquivo não suportado: {mime_type}")
        
        extension, category = cls.SUPPORTED_TYPES[mime_type]
        return cls(mime_type, extension, category)
    
    @classmethod
    def from_extension(cls, extension: str) -> "FileType":
        """Cria um FileType a partir da extensão."""
        ext = extension.lower().lstrip('.')
        
        for mime_type, (supported_ext, category) in cls.SUPPORTED_TYPES.items():
            if supported_ext == ext:
                return cls(mime_type, ext, category)
        
        raise ValueError(f"Extensão não suportada: {extension}")
    
    @classmethod
    def get_supported_extensions(cls) -> Set[str]:
        """Retorna todas as extensões suportadas."""
        return {ext for ext, _ in cls.SUPPORTED_TYPES.values()}
    
    @classmethod
    def get_supported_mime_types(cls) -> Set[str]:
        """Retorna todos os tipos MIME suportados."""
        return set(cls.SUPPORTED_TYPES.keys())
    
    @classmethod
    def get_extensions_by_category(cls, category: FileCategory) -> Set[str]:
        """Retorna extensões de uma categoria específica."""
        return {ext for ext, cat in cls.SUPPORTED_TYPES.values() if cat == category}
    
    def is_audio(self) -> bool:
        """Verifica se é um arquivo de áudio."""
        return self.category == FileCategory.AUDIO
    
    def is_image(self) -> bool:
        """Verifica se é um arquivo de imagem."""
        return self.category == FileCategory.IMAGE
    
    def is_video(self) -> bool:
        """Verifica se é um arquivo de vídeo."""
        return self.category == FileCategory.VIDEO
    
    def __str__(self) -> str:
        return f"{self.mime_type} (.{self.extension})"