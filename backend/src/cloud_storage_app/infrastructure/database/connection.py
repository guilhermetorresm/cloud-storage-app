"""
Configuração da conexão com o banco de dados PostgreSQL.
Utiliza SQLAlchemy com padrão async/await para melhor performance.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import event, pool, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from cloud_storage_app.config import get_settings


logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class para todos os modelos SQLAlchemy"""
    pass


class DatabaseManager:
    """Gerenciador de conexões com o banco de dados"""
    
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._settings = get_settings()
    
    @property
    def engine(self) -> AsyncEngine:
        """Retorna a engine do SQLAlchemy"""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Retorna a factory de sessões"""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._session_factory
    
    async def initialize(self) -> None:
        """Inicializa a conexão com o banco de dados"""
        try:
            # Configurações da engine
            engine_kwargs = {
                "url": str(self._settings.database.get_database_url()),
                "echo": self._settings.database.echo_sql,
                "pool_size": self._settings.database.pool_size,
                "max_overflow": self._settings.database.max_overflow,
                "pool_timeout": self._settings.database.pool_timeout,
                "pool_recycle": self._settings.database.pool_recycle,
                "pool_pre_ping": True,  # Verifica conexões antes de usar
                "future": True,  # Usar API futura do SQLAlchemy
            }

            
            
            # Para ambiente de teste, usar NullPool para evitar problemas
            if self._settings.app.environment == "test":
                engine_kwargs["poolclass"] = NullPool
            
            # Criar engine assíncrona com driver asyncpg
            self._engine = create_async_engine(
                engine_kwargs["url"].replace("postgresql://", "postgresql+asyncpg://"),
                **{k: v for k, v in engine_kwargs.items() if k != "url"}
            )
            
            # Configurar listeners para logging de conexões
            self._setup_engine_listeners()
            
            # Criar factory de sessões
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,  # Permite acessar objetos após commit
                autoflush=True,
                autocommit=False,
            )
            
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    def _setup_engine_listeners(self) -> None:
        """Configura listeners para a engine"""
        
        @event.listens_for(self._engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Configura parâmetros específicos do PostgreSQL se necessário"""
            if self._settings.app.debug:
                logger.debug("New database connection established")
        
        @event.listens_for(self._engine.sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log quando uma conexão é retirada do pool"""
            if self._settings.database.echo_sql:
                logger.debug("Connection checked out from pool")
        
        @event.listens_for(self._engine.sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log quando uma conexão é devolvida ao pool"""
            if self._settings.database.echo_sql:
                logger.debug("Connection checked back into pool")
    
    async def close(self) -> None:
        """Fecha todas as conexões do banco"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")
    
    async def health_check(self) -> bool:
        """Verifica se a conexão com o banco está funcionando"""
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager para obter uma sessão do banco.
        Garante que a sessão seja fechada mesmo em caso de erro.
        """
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_all_tables(self) -> None:
        """Cria todas as tabelas do banco (apenas para desenvolvimento/teste)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All database tables created")
    
    async def drop_all_tables(self) -> None:
        """Remove todas as tabelas do banco (apenas para teste)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("All database tables dropped")


# Instância global do gerenciador de banco
db_manager = DatabaseManager()


# Funções de conveniência para usar em FastAPI dependencies


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency do FastAPI para injetar sessões do banco.
    
    Usage:
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_database_session)):
            # usar db aqui
    """
    async with db_manager.get_session() as session:
        yield session


async def init_database() -> None:
    """Inicializa o banco de dados"""
    await db_manager.initialize()


async def close_database() -> None:
    """Fecha as conexões do banco de dados"""
    await db_manager.close()


# Context manager para transações
@asynccontextmanager
async def database_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager para transações explícitas.
    Automaticamente faz rollback em caso de erro.
    
    Usage:
        async with database_transaction() as session:
            # operações no banco
            await session.commit()  # commit explícito se necessário
    """
    async with db_manager.get_session() as session:
        try:
            async with session.begin():
                yield session
        except Exception:
            await session.rollback()
            raise