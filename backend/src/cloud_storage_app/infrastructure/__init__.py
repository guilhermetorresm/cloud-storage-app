"""
Infrastructure layer - External concerns
"""
from .database import *
from .auth import *
from .storage import *
from .external import FFmpegVideoProcessingService, PillowImageProcessingService, PillowThumbnailGeneratorService, MutagenAudioProcessingService

__all__ = [
    # Database
    "get_database",
    "UserModel",
    "UserRepository",
    
    # Auth
    # Add auth exports here when implemented
    
    # Storage
    # Add storage exports here when implemented
    
    # External
    # Add external service exports here when implemented
    "MutagenAudioProcessingService",
    "FFmpegVideoProcessingService",
    "PillowImageProcessingService",
    "PillowThumbnailGeneratorService",
]