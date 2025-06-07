import threading
import logging
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.infrastructure.auth.password_service import PasswordService
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService
from cloud_storage_app.application.services.password_service import PasswordApplicationService
from cloud_storage_app.infrastructure.database.connection import DatabaseManager
from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
from cloud_storage_app.application.use_cases.auth.login_use_case import LoginUseCase
from cloud_storage_app.config import get_settings

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """Container de injeção de dependência.
    
    Este container gerencia todas as dependências da aplicação seguindo o padrão de inversão de controle.
    Usa recursos nativos do dependency-injector para injeção limpa e automática.
    """
    
    # ==========================================
    # CONFIGURAÇÕES
    # ==========================================
    config = providers.Configuration()
    
    # Configurações da aplicação
    settings = providers.Singleton(get_settings)
    
    # ==========================================
    # INFRAESTRUTURA (Singleton)
    # ==========================================
    
    # Gerenciador de banco de dados
    database_manager = providers.Singleton(DatabaseManager)
    
    # Serviços de infraestrutura
    password_service = providers.Singleton(PasswordService)
    jwt_service = providers.Singleton(JWTService)
    
    # ==========================================
    # REPOSITÓRIOS (Factory)
    # ==========================================
    
    # Factory para criar UserRepository - será injetada uma sessão quando necessário
    user_repository = providers.Factory(
        UserRepository,
        # A sessão será fornecida externamente nos endpoints
    )
    
    # ==========================================
    # SERVIÇOS DE APLICAÇÃO (Factory)
    # ==========================================
    
    # Serviços de aplicação
    password_application_service = providers.Factory(
        PasswordApplicationService,
        password_service=password_service
    )

    # Casos de uso de usuário
    login_use_case = providers.Factory(
        LoginUseCase,
        password_service=password_service,
        jwt_service=jwt_service
    )


# ==========================================
# SINGLETON THREAD-SAFE
# ==========================================

_container: Optional[Container] = None
_lock = threading.Lock()


def get_container() -> Container:
    """
    Obtém a instância singleton do container de forma thread-safe.
    
    Returns:
        Container: A instância global do container
        
    Raises:
        RuntimeError: Se o container não foi inicializado
    """
    global _container
    if _container is None:
        with _lock:
            if _container is None:
                _container = Container()
                logger.info("Container inicializado")
    return _container


# ==========================================
# LIFECYCLE MANAGEMENT
# ==========================================

async def init_container() -> Container:
    """
    Inicializa o container e todos os seus recursos.
    
    Returns:
        Container: Container inicializado
    """
    container = get_container()
    
    try:
        # Inicializar recursos do container (síncrono)
        container.init_resources()
        
        # Verificar conexão com banco
        db_manager = container.database_manager()
        await db_manager.initialize()
        
        # Verificação de saúde
        is_healthy = await db_manager.health_check()
        if not is_healthy:
            raise RuntimeError("Database health check failed")
        
        logger.info("Container e recursos inicializados com sucesso")
        return container
        
    except Exception as e:
        logger.error(f"Erro ao inicializar container: {e}")
        await shutdown_container(container)
        raise


async def shutdown_container(container: Container) -> None:
    """
    Limpa recursos do container.
    
    Args:
        container: Instância do container para limpar
    """
    try:
        # Fechar conexões do banco
        db_manager = container.database_manager()
        await db_manager.close()
        
        # Limpar recursos do container (síncrono)
        container.shutdown_resources()
        
        logger.info("Container limpo com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao limpar container: {e}")


# ==========================================
# CONTEXT MANAGER PARA FASTAPI
# ==========================================

@asynccontextmanager
async def container_lifespan() -> AsyncGenerator[Container, None]:
    """
    Context manager para gerenciar o lifecycle do container.
    Ideal para usar no lifespan do FastAPI.
    """
    container = None
    try:
        container = await init_container()
        yield container
    finally:
        if container:
            await shutdown_container(container)


# ==========================================
# DEPENDENCY INJECTION HELPERS
# ==========================================

# Funções simples para injeção direta - use estas nos seus endpoints
get_user_repository = Provide[Container.user_repository]
get_password_service = Provide[Container.password_service]
get_jwt_service = Provide[Container.jwt_service]
get_password_application_service = Provide[Container.password_application_service]
get_database_manager = Provide[Container.database_manager]
get_settings_from_container = Provide[Container.settings]

# Função para obter sessão de banco (context manager)
async def get_database_session():
    """
    Dependency para obter sessão do banco de dados.
    Use como: db: AsyncSession = Depends(get_database_session)
    """
    container = get_container()
    db_manager = container.database_manager()
    
    async with db_manager.get_session() as session:
        yield session


# ==========================================
# WIRING CONFIGURATION
# ==========================================

def configure_container_wiring(container: Container) -> None:
    """
    Configura o wiring do container para os módulos da aplicação.
    
    Args:
        container: Instância do container
    """
    try:
        container.wire(modules=[
            "cloud_storage_app.presentation.api.v1.health",
            # Adicione outros módulos aqui conforme necessário
        ])
        logger.info("Container wiring configurado")
    except Exception as e:
        logger.error(f"Erro ao configurar wiring: {e}")
        raise


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

async def health_check() -> bool:
    """
    Verificação de saúde das dependências.
    
    Returns:
        bool: True se todas as dependências estão saudáveis
    """
    try:
        container = get_container()
        db_manager = container.database_manager()
        return await db_manager.health_check()
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return False