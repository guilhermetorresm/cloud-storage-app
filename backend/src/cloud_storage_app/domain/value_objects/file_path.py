import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import uuid
from typing import Optional

@dataclass(frozen=True)
class FilePath:
    """
    Objeto de Valor que representa um caminho de arquivo estruturado para o bucket.
    Formatos esperados:
    - VIDEO: user_id/videos/YYYY/MM/DD/file_id/resolution/video.ext
    - AUDIO: user_id/audios/YYYY/MM/DD/default/default/audio.ext
    - IMAGEM: user_id/images/YYYY/MM/DD/default/default/image.ext
    """
    value: str

    # Expressão regular para validar o formato do caminho.
    # Exemplo: a5b1c3d4/videos/2025/07/03/f8e7d6c5/1080p/video.mp4
    _path_regex = re.compile(
        r"^(?P<user_id>[^/]+)/"
        r"(?P<file_type>videos|audios|images)/"
        r"(?P<year>\d{4})/"
        r"(?P<month>\d{2})/"
        r"(?P<day>\d{2})/"
        r"(?P<file_id>[^/]+)/"
        r"(?P<resolution>[^/]+)/"
        r"(?P<file_name_with_ext>[^/]+)$"
    )

    def __post_init__(self):
        """
        Executado após a inicialização para validar o valor.
        Garante que o caminho não seja vazio e corresponda ao formato esperado.
        """
        if not isinstance(self.value, str) or not self.value:
            raise ValueError("O caminho do arquivo não pode ser vazio.")

        # Normaliza o caminho para usar barras '/' (padrão POSIX)
        normalized_path = str(Path(self.value).as_posix())
        # Usa object.__setattr__ para modificar o campo, já que a classe é frozen.
        object.__setattr__(self, 'value', normalized_path)

        if not self._path_regex.match(self.value):
            raise ValueError(
                f"Formato do caminho do arquivo inválido: '{self.value}'. "
                f"Esperado: 'user_id/videos|audios|images/YYYY/MM/DD/file_id/resolution/filename.ext'"
            )

    @classmethod
    def create_video(cls, user_id: uuid.UUID, file_id: str, resolution: str, 
                     file_name: str, file_date: date = None) -> "FilePath":
        """
        Factory method para criar um FilePath de vídeo.

        Args:
            user_id (uuid.UUID): O ID do usuário.
            file_id (str): O ID único do arquivo de vídeo.
            resolution (str): A resolução do vídeo (ex: '1080p', '720p', '4K').
            file_name (str): O nome do arquivo com extensão (ex: 'video.mp4').
            file_date (date, optional): A data a ser usada no caminho. 
                                        Se None, usa a data atual. Defaults to None.

        Returns:
            FilePath: Uma nova instância de FilePath para vídeo.
        """
        if not user_id or not file_id or not resolution or not file_name:
            raise ValueError("user_id, file_id, resolution e file_name não podem ser vazios.")

        today = file_date if file_date else date.today()
        
        path_str = (
            f"{str(user_id)}/videos/"
            f"{today.year}/{today.month:02d}/{today.day:02d}/"
            f"{file_id}/{resolution}/{file_name}"
        )
        
        return cls(path_str)

    @classmethod
    def create_audio(cls, user_id: uuid.UUID, file_name: str, file_date: date = None) -> "FilePath":
        """
        Factory method para criar um FilePath de áudio.

        Args:
            user_id (uuid.UUID): O ID do usuário.
            file_name (str): O nome do arquivo com extensão (ex: 'audio.mp3').
            file_date (date, optional): A data a ser usada no caminho. 
                                        Se None, usa a data atual. Defaults to None.

        Returns:
            FilePath: Uma nova instância de FilePath para áudio.
        """
        if not user_id or not file_name:
            raise ValueError("user_id e file_name não podem ser vazios.")

        today = file_date if file_date else date.today()
        
        path_str = (
            f"{str(user_id)}/audios/"
            f"{today.year}/{today.month:02d}/{today.day:02d}/"
            f"default/default/{file_name}"
        )
        
        return cls(path_str)

    @classmethod
    def create_image(cls, user_id: uuid.UUID, file_name: str, file_date: date = None) -> "FilePath":
        """
        Factory method para criar um FilePath de imagem.

        Args:
            user_id (uuid.UUID): O ID do usuário.
            file_name (str): O nome do arquivo com extensão (ex: 'image.png').
            file_date (date, optional): A data a ser usada no caminho. 
                                        Se None, usa a data atual. Defaults to None.

        Returns:
            FilePath: Uma nova instância de FilePath para imagem.
        """
        if not user_id or not file_name:
            raise ValueError("user_id e file_name não podem ser vazios.")

        today = file_date if file_date else date.today()
        
        path_str = (
            f"{str(user_id)}/images/"
            f"{today.year}/{today.month:02d}/{today.day:02d}/"
            f"default/default/{file_name}"
        )
        
        return cls(path_str)

    @classmethod
    def create(cls, user_id: uuid.UUID, file_type: str, file_name: str, 
               file_date: date = None, file_id: str = None, resolution: str = None) -> "FilePath":
        """
        Factory method genérico para criar um FilePath baseado no tipo de arquivo.

        Args:
            user_id (uuid.UUID): O ID do usuário.
            file_type (str): O tipo do arquivo ('videos', 'audios', 'images').
            file_name (str): O nome do arquivo com extensão.
            file_date (date, optional): A data a ser usada no caminho. Defaults to None.
            file_id (str, optional): O ID do arquivo (apenas para vídeos). Defaults to None.
            resolution (str, optional): A resolução (apenas para vídeos). Defaults to None.

        Returns:
            FilePath: Uma nova instância de FilePath.
        """
        if file_type == 'videos':
            if not file_id or not resolution:
                raise ValueError("file_id e resolution são obrigatórios para vídeos.")
            return cls.create_video(user_id, file_id, resolution, file_name, file_date)
        elif file_type == 'audios':
            return cls.create_audio(user_id, file_name, file_date)
        elif file_type == 'images':
            return cls.create_image(user_id, file_name, file_date)
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")

    def _get_match_group(self, group_name: str) -> str:
        """Helper para extrair partes do caminho usando o regex."""
        match = self._path_regex.match(self.value)
        if not match:
            # Esta exceção nunca deveria acontecer se o __post_init__ funcionar.
            raise RuntimeError("Não foi possível analisar o caminho, apesar de ter passado na validação.")
        return match.group(group_name)

    @property
    def user_id(self) -> uuid.UUID:
        """Retorna o ID do usuário (user_id) do caminho."""
        return uuid.UUID(self._get_match_group('user_id'))

    @property
    def file_type(self) -> str:
        """Retorna o tipo de arquivo do caminho (videos, audios, images)."""
        return self._get_match_group('file_type')
        
    @property
    def creation_date(self) -> date:
        """Retorna a data (ano, mês, dia) extraída do caminho."""
        year = int(self._get_match_group('year'))
        month = int(self._get_match_group('month'))
        day = int(self._get_match_group('day'))
        return date(year, month, day)

    @property
    def file_id(self) -> str:
        """Retorna o ID do arquivo (para vídeos) ou 'default' (para áudios e imagens)."""
        return self._get_match_group('file_id')

    @property
    def resolution(self) -> str:
        """Retorna a resolução do vídeo ou 'default' para áudios e imagens."""
        return self._get_match_group('resolution')

    @property
    def file_name_with_ext(self) -> str:
        """Retorna o nome do arquivo com extensão."""
        return self._get_match_group('file_name_with_ext')

    @property
    def extension(self) -> str:
        """Retorna a extensão do arquivo em minúsculas."""
        return Path(self.file_name_with_ext).suffix.lower()

    @property
    def is_video(self) -> bool:
        """Verifica se o arquivo é um vídeo."""
        return self.file_type == 'videos'

    @property
    def is_audio(self) -> bool:
        """Verifica se o arquivo é um áudio."""
        return self.file_type == 'audios'

    @property
    def is_image(self) -> bool:
        """Verifica se o arquivo é uma imagem."""
        return self.file_type == 'images'

    def __str__(self) -> str:
        """Retorna a representação em string do caminho."""
        return self.value