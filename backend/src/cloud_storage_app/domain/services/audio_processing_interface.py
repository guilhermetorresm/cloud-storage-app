from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple, Set
from io import BytesIO


class AudioProcessingService(ABC):
    """
    Interface para serviços de processamento de áudio.
    
    Define os métodos para extração de metadados, análise de propriedades
    e outras operações de processamento de arquivos de áudio.
    """
    
    @abstractmethod
    async def extract_metadata(self, audio_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extrai metadados de um arquivo de áudio.
        
        Args:
            audio_data: Dados binários do arquivo de áudio
            filename: Nome do arquivo
            
        Returns:
            Dict contendo os metadados extraídos do arquivo de áudio:
            - duration_seconds: Duração em segundos
            - bitrate: Taxa de bits em kbps
            - sample_rate: Taxa de amostragem em Hz
            - channels: Número de canais (1=mono, 2=estéreo)
            - genre: Gênero musical (se disponível)
            - title: Título da música (se disponível)
            - artist: Artista (se disponível)
            - album: Álbum (se disponível)
            - year: Ano (se disponível)
            - codec: Codec utilizado
            - file_format: Formato do arquivo
        """
        pass
    
    @abstractmethod
    async def validate_audio_integrity(self, audio_data: bytes) -> bool:
        """
        Valida a integridade de um arquivo de áudio.
        
        Args:
            audio_data: Dados binários do arquivo de áudio
            
        Returns:
            True se o arquivo é válido, False caso contrário
        """
        pass
    
    @abstractmethod
    async def get_audio_duration(self, audio_data: bytes) -> Optional[float]:
        """
        Obtém a duração de um arquivo de áudio em segundos.
        
        Args:
            audio_data: Dados binários do arquivo de áudio
            
        Returns:
            Duração em segundos ou None se não puder ser determinada
        """
        pass
    
    @abstractmethod
    async def extract_audio_properties(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extrai propriedades técnicas do áudio.
        
        Args:
            audio_data: Dados binários do arquivo de áudio
            
        Returns:
            Dict contendo propriedades técnicas:
            - bitrate: Taxa de bits
            - sample_rate: Taxa de amostragem
            - channels: Número de canais
            - codec: Codec utilizado
            - is_lossy: Se é compressão com perda
            - quality_score: Pontuação de qualidade (0-100)
        """
        pass
    
    @abstractmethod
    async def extract_id3_tags(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extrai tags ID3 de um arquivo de áudio.
        
        Args:
            audio_data: Dados binários do arquivo de áudio
            
        Returns:
            Dict contendo as tags ID3 extraídas
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> Set[str]:
        """
        Retorna os formatos de áudio suportados.
        
        Returns:
            Set com os formatos suportados
        """
        pass
    
    @abstractmethod
    def is_format_supported(self, format_name: str) -> bool:
        """
        Verifica se um formato é suportado.
        
        Args:
            format_name: Nome do formato (extensão)
            
        Returns:
            True se o formato é suportado
        """
        pass
    
    @abstractmethod
    def is_audio_format_valid_for_entity(self, format_name: str) -> bool:
        """
        Verifica se o formato é válido para a entidade AudioFile.
        
        Args:
            format_name: Nome do formato
            
        Returns:
            True se o formato é válido para AudioFile
        """
        pass