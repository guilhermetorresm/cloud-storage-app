from pydantic import BaseModel, Field, validator
from typing import IO, Any, Optional, List, Dict
from uuid import UUID
from datetime import datetime
import re

def validate_tag(tag: str) -> str:
    """Valida uma tag individual de acordo com as regras de negócio"""
    if not tag:
        raise ValueError("Tag não pode estar vazia")
    
    # Validação de comprimento
    if not (1 <= len(tag) <= 50):
        raise ValueError("Tag deve ter entre 1 e 50 caracteres")
    
    # Validação de caracteres permitidos
    tag_pattern = r'^[A-Za-zÀ-ÿ\s-]+$'
    if not re.match(tag_pattern, tag):
        raise ValueError("Tag deve conter apenas letras, espaços e hífens")
    
    return tag.strip()

class UploadFileInputDTO(BaseModel):
    file_name: str
    file_size: int
    mime_type: str
    file_object: IO[Any] # O objeto do arquivo em si
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    tags: Optional[List[str]] = Field(default_factory=list) # Lista de tags opcional

    @validator('tags', pre=True)
    def validate_tags(cls, v):
        """Valida a lista de tags"""
        if v is None:
            return []
        
        if not isinstance(v, list):
            raise ValueError("Tags deve ser uma lista")
        
        # Remove duplicatas e valida cada tag
        validated_tags = []
        seen_tags = set()
        
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("Cada tag deve ser uma string")
            
            validated_tag = validate_tag(tag)
            
            # Verifica duplicatas (case-insensitive)
            if validated_tag.lower() in seen_tags:
                continue
            
            seen_tags.add(validated_tag.lower())
            validated_tags.append(validated_tag)
        
        return validated_tags

    class Config:
        arbitrary_types_allowed = True # Necessário para IO[Any]


class ListUserFilesInputDTO(BaseModel):
    user_id: UUID
    page: int = Field(1, gt=0)
    page_size: int = Field(20, gt=0, le=100)
    file_type: Optional[str] = None # Filtro opcional: "image", "audio", "video"
    tags: Optional[List[str]] = Field(default_factory=list) # Filtro por tags
    file_name: Optional[str] = None # Filtro por nome do arquivo

    @validator('tags', pre=True)
    def validate_filter_tags(cls, v):
        """Valida as tags de filtro"""
        if v is None:
            return []
        
        if not isinstance(v, list):
            raise ValueError("Tags deve ser uma lista")
        
        # Para filtros, aceitamos tags parciais (não precisam ser exatas)
        validated_tags = []
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("Cada tag deve ser uma string")
            
            tag = tag.strip()
            if tag:  # Aceita qualquer tag não vazia para filtro
                validated_tags.append(tag)
        
        return validated_tags


class GetFileDetailsInputDTO(BaseModel):
    file_id: UUID


class UpdateFileMetadataInputDTO(BaseModel):
    file_id: UUID
    new_name: Optional[str] = Field(None, min_length=1, max_length=255)
    new_description: Optional[str] = Field(None, min_length=1, max_length=500)
    new_tags: Optional[List[str]] = Field(default_factory=list) # Nova lista de tags

    @validator('new_tags', pre=True)
    def validate_new_tags(cls, v):
        """Valida a nova lista de tags"""
        if v is None:
            return []
        
        if not isinstance(v, list):
            raise ValueError("Tags deve ser uma lista")
        
        # Remove duplicatas e valida cada tag
        validated_tags = []
        seen_tags = set()
        
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("Cada tag deve ser uma string")
            
            validated_tag = validate_tag(tag)
            
            # Verifica duplicatas (case-insensitive)
            if validated_tag.lower() in seen_tags:
                continue
            
            seen_tags.add(validated_tag.lower())
            validated_tags.append(validated_tag)
        
        return validated_tags


class DeleteFileInputDTO(BaseModel):
    file_id: UUID


# Response 
class FileResponseDTO(BaseModel):
    """DTO para resposta de arquivos"""
    file_id: str
    name: str
    description: Optional[str] = None
    file_type: str
    mime_type: str
    extension: str
    category: str
    size: int
    size_humanized: str
    tags: List[str] = []
    path: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    has_thumbnail: bool = False

    class Config:
        from_attributes = True


class FileListResponseDTO(BaseModel):
    """DTO para resposta de lista de arquivos"""
    files: List[FileResponseDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class FileUploadResponseDTO(BaseModel):
    """DTO para resposta de upload de arquivo"""
    file_id: str
    name: str
    description: Optional[str] = None
    file_type: str
    mime_type: str
    size: int
    size_humanized: str
    tags: List[str] = []
    upload_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ImageFileOutputDTO(FileResponseDTO):
    """DTO específico para arquivos de imagem"""
    # Dimensões
    width: Optional[int] = None
    height: Optional[int] = None
    dimensions: Optional[str] = None  # ex: "1920x1080"
    aspect_ratio: Optional[float] = None
    megapixels: Optional[float] = None
    
    # Metadados técnicos
    color_depth: Optional[int] = None
    dpi: Optional[int] = None
    has_transparency: Optional[bool] = None
    compression: Optional[str] = None
    
    # Metadados da câmera
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    taken_at: Optional[str] = None  # Data/hora da foto em formato ISO
    
    # Dados GPS
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    has_gps_data: bool = False
    

class AudioFileOutputDTO(FileResponseDTO):
    """DTO específico para arquivos de áudio"""
    # Duração
    duration_seconds: Optional[int] = None
    duration_formatted: Optional[str] = None  # ex: "03:45"
    
    # Metadados técnicos
    bitrate: Optional[int] = None  # kbps
    sample_rate: Optional[int] = None  # Hz
    channels: Optional[int] = None
    
    # Metadados de gênero
    genre: Optional[str] = None


class VideoFileOutputDTO(FileResponseDTO):
    """DTO específico para arquivos de vídeo"""
    # Duração
    duration_seconds: Optional[int] = None
    duration_formatted: Optional[str] = None  # ex: "01:23:45"
    
    # Dimensões e resolução
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[str] = None  # ex: "1920x1080"
    aspect_ratio: Optional[float] = None
    quality_level: Optional[str] = None  # ex: "Full HD", "4K/UHD"
    
    # Metadados técnicos
    frame_rate: Optional[float] = None  # fps
    estimated_frames: Optional[int] = None
    bitrate: Optional[int] = None  # kbps
    
    # Codecs
    codec: Optional[str] = None
    audio_codec: Optional[str] = None
    
    # Características
    has_audio: Optional[bool] = None
    has_subtitles: Optional[bool] = None
    created_with: Optional[str] = None  # Software usado para criar
    
    # Metadados de gênero
    genre: Optional[str] = None
    
    # Versões do vídeo
    versions_count: int = 0
    has_versions: bool = False
    original_version: Optional[str] = None
    available_resolutions: List[str] = []
    versions: Dict[str, dict] = {}  # Detalhes das versões


class FileDetailsOutputDTO(BaseModel):
    """DTO para detalhes completos de um arquivo"""
    metadata: FileResponseDTO | ImageFileOutputDTO | AudioFileOutputDTO | VideoFileOutputDTO
    download_url: Optional[str] = None


# Métodos auxiliares para conversão de entidades para DTOs
def entity_to_file_response_dto(file_entity) -> FileResponseDTO:
    """Converte qualquer entidade de arquivo para FileResponseDTO"""
    return FileResponseDTO(
        file_id=str(file_entity.file_id.value),
        name=file_entity.name.value,
        description=file_entity.description.value if file_entity.description else None,
        file_type=file_entity.file_type.mime_type,
        mime_type=file_entity.file_type.mime_type,
        extension=file_entity.file_type.extension,
        category=file_entity.file_type.category.value,
        size=file_entity.size.value,
        size_humanized=str(file_entity.size),
        tags=[tag.value for tag in file_entity.tags],
        path=file_entity.path.value,
        is_deleted=file_entity.is_deleted,
        created_at=file_entity.created_at,
        updated_at=file_entity.updated_at,
        last_accessed_at=file_entity.last_accessed_at
    )


def image_entity_to_dto(image_entity) -> ImageFileOutputDTO:
    """Converte entidade ImageFile para ImageFileOutputDTO"""
    base_dto = entity_to_file_response_dto(image_entity)
    
    return ImageFileOutputDTO(
        **base_dto.dict(),
        width=image_entity.width,
        height=image_entity.height,
        dimensions=image_entity.dimensions,
        aspect_ratio=image_entity.aspect_ratio,
        megapixels=image_entity.megapixels,
        color_depth=image_entity.color_depth,
        dpi=image_entity.dpi,
        has_transparency=image_entity.has_transparency,
        compression=image_entity.compression,
        camera_make=image_entity.camera_make,
        camera_model=image_entity.camera_model,
        taken_at=image_entity.taken_at,
        gps_latitude=image_entity.gps_latitude,
        gps_longitude=image_entity.gps_longitude,
        has_gps_data=image_entity.has_gps_data,
        thumbnail_path=image_entity.thumbnail.value if image_entity.thumbnail else None,
        has_thumbnail=image_entity.has_thumbnail
    )


def audio_entity_to_dto(audio_entity) -> AudioFileOutputDTO:
    """Converte entidade AudioFile para AudioFileOutputDTO"""
    base_dto = entity_to_file_response_dto(audio_entity)
    
    return AudioFileOutputDTO(
        **base_dto.dict(),
        duration_seconds=audio_entity.duration_seconds,
        duration_formatted=audio_entity.duration_formatted,
        bitrate=audio_entity.bitrate,
        sample_rate=audio_entity.sample_rate,
        channels=audio_entity.channels,
        genre=audio_entity.genre
    )


def video_entity_to_dto(video_entity) -> VideoFileOutputDTO:
    """Converte entidade VideoFile para VideoFileOutputDTO"""
    base_dto = entity_to_file_response_dto(video_entity)
    
    # Preparar dados das versões
    versions_data = {}
    for resolution, version in video_entity._versions.items():
        versions_data[resolution] = {
            'file_path': str(version.file_path),
            'is_original': version.is_original,
            'processing_status': version.processing_status,
            'is_ready': version.is_ready
        }
    
    return VideoFileOutputDTO(
        **base_dto.dict(),
        duration_seconds=video_entity.duration_seconds,
        duration_formatted=video_entity.duration_formatted,
        width=video_entity.width,
        height=video_entity.height,
        resolution=video_entity.resolution,
        aspect_ratio=video_entity.aspect_ratio,
        quality_level=video_entity.quality_level,
        frame_rate=video_entity.frame_rate,
        estimated_frames=video_entity.estimated_frames,
        bitrate=video_entity.bitrate,
        codec=video_entity.codec,
        audio_codec=video_entity.audio_codec,
        has_audio=video_entity.has_audio,
        has_subtitles=video_entity.has_subtitles,
        created_with=video_entity.created_with,
        genre=video_entity.genre,
        thumbnail_path=video_entity.thumbnail.value if video_entity.thumbnail else None,
        has_thumbnail=video_entity.has_thumbnail,
        versions_count=video_entity.versions_count,
        has_versions=video_entity.has_versions,
        original_version=video_entity._original_version,
        available_resolutions=video_entity.get_available_versions(),
        versions=versions_data
    )


def entity_to_specific_dto(file_entity):
    """Converte entidade para o DTO específico baseado no tipo"""
    if hasattr(file_entity, 'is_audio') and file_entity.is_audio:
        return audio_entity_to_dto(file_entity)
    elif hasattr(file_entity, 'is_image') and file_entity.is_image:
        return image_entity_to_dto(file_entity)
    elif hasattr(file_entity, 'is_video') and file_entity.is_video:
        return video_entity_to_dto(file_entity)
    else:
        return entity_to_file_response_dto(file_entity)