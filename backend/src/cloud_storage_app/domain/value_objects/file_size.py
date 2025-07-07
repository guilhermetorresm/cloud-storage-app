from dataclasses import dataclass


@dataclass(frozen=True)
class FileSize:
    """Value Object para tamanho de arquivo em bytes."""
    
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Tamanho do arquivo não pode ser negativo")
        
        # Limite máximo de 500MB para arquivos
        max_size = 500 * 1024 * 1024  # 500MB em bytes
        if self.value > max_size:
            raise ValueError(f"Tamanho do arquivo excede o limite máximo de {max_size} bytes")
    
    @property
    def bytes(self) -> int:
        """Retorna o tamanho em bytes"""
        return self.value
    
    @property
    def kilobytes(self) -> float:
        """Retorna o tamanho em kilobytes"""
        return self.value / 1024
    
    @property
    def megabytes(self) -> float:
        """Retorna o tamanho em megabytes"""
        return self.value / (1024 * 1024)
    
    @property
    def gigabytes(self) -> float:
        """Retorna o tamanho em gigabytes"""
        return self.value / (1024 * 1024 * 1024)
    
    def humanize(self) -> str:
        """Retorna o tamanho em formato legível."""
        if self.value < 1024:
            return f"{self.value} B"
        elif self.value < 1024 * 1024:
            return f"{self.kilobytes:.1f} KB"
        elif self.value < 1024 * 1024 * 1024:
            return f"{self.megabytes:.1f} MB"
        else:
            return f"{self.gigabytes:.1f} GB"
    
    def __str__(self) -> str:
        return self.humanize()
