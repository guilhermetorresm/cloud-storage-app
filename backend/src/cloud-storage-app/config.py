"""
Configurações da aplicação Cloud Storage.
Utiliza Pydantic Settings para validação e carregamento de variáveis de ambiente.
"""

from functools import lru_cache
from typing import Optional
from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Configurações específicas do banco de dados"""
    
    # Configurações individuais do PostgreSQL
    postgres_server: str = Field(default="localhost", env="POSTGRES_SERVER")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="cloud_storage_db", env="POSTGRES_DB")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    
    # URL completa do banco (opcional, sobrescreve as configurações individuais)
    database_url: Optional[PostgresDsn] = Field(default=None, env="DATABASE_URL")
    
    # Configurações do pool de conexões
    pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")  # 1 hora
    
    # Configurações de debug e logging
    echo_sql: bool = Field(default=False, env="DB_ECHO_SQL")
    
    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Constrói a URL do banco se não foi fornecida diretamente"""
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",  # Driver assíncrono
            username=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_server"),
            port=values.get("postgres_port"),
            path=f"/{values.get('postgres_db') or ''}"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# class AuthSettings(BaseSettings):
#     """Configurações de autenticação"""
    
#     secret_key: str = Field(env="SECRET_KEY")
#     algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
#     access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
#     refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False


# class StorageSettings(BaseSettings):
#     """Configurações de armazenamento S3"""
    
#     aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
#     aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
#     aws_region: str = Field(default="us-east-1", env="AWS_REGION")
#     s3_bucket_name: str = Field(env="S3_BUCKET_NAME")
#     s3_endpoint_url: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")  # Para MinIO local
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False


class AppSettings(BaseSettings):
    """Configurações gerais da aplicação"""
    
    app_name: str = Field(default="Cloud Storage API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # em segundos
    
    # Upload limits
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    allowed_file_types: list[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".txt"],
        env="ALLOWED_FILE_TYPES"
    )
    
    @validator("allowed_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class Settings(BaseSettings):
    """Configurações principais que agregam todas as outras"""
    
    database: DatabaseSettings = DatabaseSettings()
    auth: AuthSettings = AuthSettings()
    storage: StorageSettings = StorageSettings()
    app: AppSettings = AppSettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação com cache.
    Usar @lru_cache() garante que as configurações sejam carregadas apenas uma vez.
    """
    return Settings()


# Instância global das configurações
settings = get_settings()