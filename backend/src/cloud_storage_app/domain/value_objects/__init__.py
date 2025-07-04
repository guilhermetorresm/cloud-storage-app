"""
Domain value objects
"""
from .email import Email
from .first_name import FirstName
from .last_name import LastName
from .username import Username
from .password import Password
from .hashed_password import HashedPassword
from .user_id import UserId
from .user_description import UserDescription
from .profile_picture import ProfilePicture
from .file_id import FileId
from .file_name import FileName
from .file_path import FilePath
from .file_size import FileSize
from .file_type import FileType
from .file_description import FileDescription
from .tag import Tag

__all__ = [
    "Email",
    "FirstName", 
    "LastName",
    "Username",
    "Password",
    "HashedPassword",
    "UserId",
    "UserDescription",
    "ProfilePicture",
    "FileId",
    "FileName",
    "FilePath",
    "FileSize",
    "FileType",
    "FileDescription",
    "Tag",
]