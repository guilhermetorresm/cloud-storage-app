from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from io import BytesIO
from PIL.Image import Image


class ImageProcessingService(ABC):
    """
    Interface para serviços de processamento de imagens.
    
    Define os métodos para extração de metadados, geração de thumbnails
    e outras operações de processamento de imagens.
    """
    
    @abstractmethod
    async def extract_metadata(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extrai metadados de uma imagem.
        
        Args:
            image_data: Dados binários da imagem
            filename: Nome do arquivo
            
        Returns:
            Dict contendo os metadados extraídos da imagem
        """
        pass
    
    @abstractmethod
    async def generate_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (200, 150)) -> bytes:
        """
        Gera uma miniatura da imagem.
        
        Args:
            image_data: Dados binários da imagem original
            size: Tupla com largura e altura da miniatura
            
        Returns:
            Dados binários da miniatura gerada
        """
        pass
    
    @abstractmethod
    async def validate_image_integrity(self, image_data: bytes) -> bool:
        """
        Valida a integridade de uma imagem.
        
        Args:
            image_data: Dados binários da imagem
            
        Returns:
            True se a imagem é válida, False caso contrário
        """
        pass
    
    @abstractmethod
    async def get_image_dimensions(self, image_data: bytes) -> Tuple[int, int]:
        """
        Obtém as dimensões de uma imagem.
        
        Args:
            image_data: Dados binários da imagem
            
        Returns:
            Tupla com largura e altura da imagem
        """
        pass
    
    @abstractmethod
    async def extract_exif_data(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extrai dados EXIF de uma imagem.
        
        Args:
            image_data: Dados binários da imagem
            
        Returns:
            Dict contendo os dados EXIF extraídos
        """
        pass