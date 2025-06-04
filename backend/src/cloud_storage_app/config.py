"""
Configurações da aplicação Cloud Storage.
Utiliza Pydantic Settings para validação e carregamento de variáveis de ambiente.
"""

import logging
import os
from functools import lru_cache
from typing import Optional, List, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import json
from pathlib import Path


# Configuração do logger
logger = logging.getLogger(__name__)



class DatabaseSettings(BaseSettings):
    """Configurações específicas do banco de dados"""
    
    # Configurações individuais do PostgreSQL
    postgres_server: str = Field(default="db", env="POSTGRES_SERVER")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="cloud_storage_db", env="POSTGRES_DB")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")

    # URL completa do banco (opcional, sobrescreve as configurações individuais)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")

    # Configurações do pool de conexões
    pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")  # 1 hora
    
    # Configurações de debug e logging
    echo_sql: bool = Field(default=False, env="DB_ECHO_SQL")
    
    def get_database_url(self) -> str:
        """Constrói a URL do banco se não foi fornecida diretamente"""
        if self.database_url:
            # Garante que a URL use o driver asyncpg
            if not self.database_url.startswith("postgresql+asyncpg://"):
                return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
            return self.database_url
        
        # Constrói a URL com o driver asyncpg
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }
    

class AuthSettings(BaseSettings):
    """Configurações de autenticação"""
    
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    model_config = model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


class StorageSettings(BaseSettings):
    """Configurações de armazenamento S3"""
    
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    s3_bucket_name: str = Field(env="S3_BUCKET_NAME")
    s3_endpoint_url: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")  # Para MinIO local
    
    model_config = model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

class AppSettings(BaseSettings):
    # Informações da aplicação
    app_name: str = Field(default="Cloud Storage API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # CORS - Origins permitidas (como string para evitar parse automático do JSON)
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Configurações de upload
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    allowed_file_types: str = Field(
        default=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.zip,.rar",
        env="ALLOWED_FILE_TYPES"
    )
    
    @field_validator('allowed_origins', mode='after')
    @classmethod
    def parse_allowed_origins(cls, v: str) -> List[str]:
        """Parse ALLOWED_ORIGINS de string separada por vírgula"""
        if not v or v.strip() == "":
            return ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
        
        # Parse como string separada por vírgula
        origins = [origin.strip() for origin in v.split(',') if origin.strip()]
        return origins if origins else ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    
    @field_validator('allowed_file_types', mode='after')
    @classmethod
    def parse_allowed_file_types(cls, v: str) -> List[str]:
        """Parse ALLOWED_FILE_TYPES de string separada por vírgula"""
        if not v or v.strip() == "":
            return [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".txt", ".zip", ".rar"]
        
        # Parse como string separada por vírgula
        types = [file_type.strip() for file_type in v.split(',') if file_type.strip()]
        return types if types else [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".txt", ".zip", ".rar"]
    
    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        """Parse DEBUG de string para boolean"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v) if v is not None else False
    
    def get_allowed_origins(self) -> List[str]:
        """Retorna as origins permitidas como lista"""
        return self.allowed_origins
    
    def get_allowed_file_types(self) -> List[str]:
        """Retorna os tipos de arquivo permitidos como lista"""
        return self.allowed_file_types
    
    model_config = model_config = model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


class Settings(BaseSettings):
    """Configurações principais que agregam todas as outras"""
    
    # Não instancie as classes aqui, deixe o Pydantic fazer isso
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    app: AppSettings = Field(default_factory=AppSettings)
    
    model_config = model_config = model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação com cache.
    Usar @lru_cache() garante que as configurações sejam carregadas apenas uma vez.
    """
    settings = Settings()
    
    # Log das configurações carregadas
    logger.info("Configurações carregadas:")
    logger.info(f"Database URL: {settings.database.get_database_url()}")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Debug mode: {settings.app.debug}")
    logger.info(f"Database Server: {settings.database.postgres_server}")
    logger.info(f"Database Name: {settings.database.postgres_db}")
    logger.info(f"Database User: {settings.database.postgres_user}")
    
    return settings


# Instância global das configurações
settings = get_settings()