from dataclasses import dataclass
from typing import Optional, List
from .base_file import BaseFile
from ..value_objects import Tag, FilePath


@dataclass
class ImageFile(BaseFile):
    """
    Entidade para arquivos de imagem.
    
    Estende BaseFile com metadados específicos de imagem.
    """
    
    # Metadados específicos de imagem
    _width: Optional[int] = None
    _height: Optional[int] = None
    _color_depth: Optional[int] = None
    _dpi: Optional[int] = None
    _has_transparency: Optional[bool] = None
    _compression: Optional[str] = None
    _camera_make: Optional[str] = None
    _camera_model: Optional[str] = None
    _taken_at: Optional[str] = None  # Data/hora da foto em formato ISO
    _gps_latitude: Optional[float] = None
    _gps_longitude: Optional[float] = None

    _thumbnail: Optional[FilePath] = None
    
    def __post_init__(self):
        """Validações específicas de imagem"""
        super().__post_init__()
        
        if not self.is_valid_file_type():
            raise ValueError("Tipo de arquivo inválido para ImageFile")
    
    @classmethod
    def create(cls, owner_id, name: str, path: str, size: int, 
               description: str, tags: List[str], width: Optional[int] = None,
               height: Optional[int] = None, color_depth: Optional[int] = None,
               dpi: Optional[int] = None,
               has_transparency: Optional[bool] = None,
               compression: Optional[str] = None,
               camera_make: Optional[str] = None,
               camera_model: Optional[str] = None,
               taken_at: Optional[str] = None,
               gps_latitude: Optional[float] = None,
               gps_longitude: Optional[float] = None) -> "ImageFile":
        
        tags_list = [Tag(tag) for tag in tags]
        """Cria um novo arquivo de imagem"""
        return super().create(
            owner_id=owner_id,
            name=name,
            path=path,
            size=size,
            description=description,
            tags=tags_list,
            _width=width,
            _height=height,
            _color_depth=color_depth,
            _dpi=dpi,
            _has_transparency=has_transparency,
            _compression=compression,
            _camera_make=camera_make,
            _camera_model=camera_model,
            _taken_at=taken_at,
            _gps_latitude=gps_latitude,
            _gps_longitude=gps_longitude
        )
    
    # Getters para metadados de imagem
    @property
    def width(self) -> Optional[int]:
        return self._width
    
    @property
    def height(self) -> Optional[int]:
        return self._height
    
    @property
    def color_depth(self) -> Optional[int]:
        return self._color_depth
    
    @property
    def dpi(self) -> Optional[int]:
        return self._dpi
    
    @property
    def has_transparency(self) -> Optional[bool]:
        return self._has_transparency
    
    @property
    def compression(self) -> Optional[str]:
        return self._compression
    
    @property
    def camera_make(self) -> Optional[str]:
        return self._camera_make
    
    @property
    def camera_model(self) -> Optional[str]:
        return self._camera_model
    
    @property
    def taken_at(self) -> Optional[str]:
        return self._taken_at
    
    @property
    def gps_latitude(self) -> Optional[float]:
        return self._gps_latitude
    
    @property
    def gps_longitude(self) -> Optional[float]:
        return self._gps_longitude
    
    @property
    def dimensions(self) -> str:
        """Retorna as dimensões formatadas"""
        if self._width is None or self._height is None:
            return "Desconhecido"
        return f"{self._width}x{self._height}"
    
    @property
    def aspect_ratio(self) -> Optional[float]:
        """Retorna a proporção da imagem"""
        if self._width is None or self._height is None or self._height == 0:
            return None
        return self._width / self._height
    
    @property
    def megapixels(self) -> Optional[float]:
        """Retorna o número de megapixels"""
        if self._width is None or self._height is None:
            return None
        return (self._width * self._height) / 1000000
    
    @property
    def has_gps_data(self) -> bool:
        """Verifica se a imagem possui dados GPS"""
        return self._gps_latitude is not None and self._gps_longitude is not None
    
    # Métodos de domínio específicos
    def update_metadata(self, width: Optional[int] = None,
                       height: Optional[int] = None,
                       color_depth: Optional[int] = None,
                       has_transparency: Optional[bool] = None,
                       compression: Optional[str] = None,
                       camera_make: Optional[str] = None,
                       camera_model: Optional[str] = None,
                       taken_at: Optional[str] = None,
                       gps_latitude: Optional[float] = None,
                       gps_longitude: Optional[float] = None) -> None:
        """Atualiza os metadados do arquivo de imagem"""
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height
        if color_depth is not None:
            self._color_depth = color_depth
        if has_transparency is not None:
            self._has_transparency = has_transparency
        if compression is not None:
            self._compression = compression
        if camera_make is not None:
            self._camera_make = camera_make
        if camera_model is not None:
            self._camera_model = camera_model
        if taken_at is not None:
            self._taken_at = taken_at
        if gps_latitude is not None:
            self._gps_latitude = gps_latitude
        if gps_longitude is not None:
            self._gps_longitude = gps_longitude
        
        self._mark_as_updated()
    
    def remove_gps_data(self) -> None:
        """Remove os dados GPS da imagem por motivos de privacidade"""
        self._gps_latitude = None
        self._gps_longitude = None
        self._mark_as_updated()
    
    def get_metadata(self) -> dict:
        """Retorna metadados específicos do arquivo de imagem"""
        return {
            'width': self._width,
            'height': self._height,
            'dimensions': self.dimensions,
            'aspect_ratio': self.aspect_ratio,
            'megapixels': self.megapixels,
            'color_depth': self._color_depth,
            'has_transparency': self._has_transparency,
            'compression': self._compression,
            'camera_make': self._camera_make,
            'camera_model': self._camera_model,
            'taken_at': self._taken_at,
            'has_gps_data': self.has_gps_data,
            'gps_latitude': self._gps_latitude,
            'gps_longitude': self._gps_longitude,
            'thumbnail': {
                'has_thumbnail': self.has_thumbnail,
                'path': str(self._thumbnail) if self._thumbnail else None
            }
        }
    
    def is_valid_file_type(self) -> bool:
        """Verifica se o tipo de arquivo é válido para imagem"""
        return self._file_type.is_image
    
    # Métodos para gerenciamento de thumbnails
    @property
    def thumbnail(self) -> Optional[FilePath]:
        """Retorna o caminho do thumbnail do vídeo"""
        return self._thumbnail
    
    @property
    def has_thumbnail(self) -> bool:
        """Verifica se o vídeo tem thumbnail"""
        return self._thumbnail is not None
    
    def set_thumbnail(self, thumbnail_path: str) -> None:
        """Define o thumbnail do vídeo"""
        self._thumbnail = FilePath(thumbnail_path)
        self._mark_as_updated()
    
    def remove_thumbnail(self) -> None:
        """Remove o thumbnail do vídeo"""
        self._thumbnail = None
        self._mark_as_updated()
    
    def generate_thumbnail_path(self) -> FilePath:
        """Gera o caminho padrão para o thumbnail do vídeo"""
        import uuid
        from datetime import date
        
        return FilePath.create_thumbnail(
            user_id=uuid.UUID(str(self._owner_id)),
            file_id=str(self._file_id),
            file_name=self._name.value,
            file_type="images",
            file_date=date.today()
        )
