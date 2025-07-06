from abc import ABC, abstractmethod
from typing import IO, Optional, Dict, Any
from ..value_objects import FilePath

class IStorageService(ABC):
    """
    Interface para o serviço de armazenamento de arquivos (Domain Layer).
    Define as operações de armazenamento independentemente da tecnologia.
    """

    @abstractmethod
    async def upload_file(self, file_object: IO[Any], file_path: FilePath, mime_type: str) -> None:
        """
        Faz o upload de um objeto de arquivo para o serviço de armazenamento.

        Args:
            file_object: O objeto de arquivo binário para upload.
            file_path: O caminho (chave) onde o arquivo será armazenado.
            mime_type: O tipo MIME do arquivo.
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: FilePath) -> None:
        """
        Deleta um arquivo do serviço de armazenamento.

        Args:
            file_path: O caminho (chave) do arquivo a ser deletado.
        """
        pass

    @abstractmethod
    async def get_presigned_url(self, file_path: FilePath, expiration: int = 3600) -> Optional[str]:
        """
        Gera uma URL pré-assinada para acesso temporário a um arquivo.

        Args:
            file_path: O caminho (chave) do arquivo.
            expiration: Tempo de expiração da URL em segundos.

        Returns:
            A URL pré-assinada ou None se o arquivo não existir.
        """
        pass

    @abstractmethod
    async def file_exists(self, file_path: FilePath) -> bool:
        """
        Verifica se um arquivo existe no serviço de armazenamento.

        Args:
            file_path: O caminho (chave) do arquivo.

        Returns:
            True se o arquivo existe, False caso contrário.
        """
        pass