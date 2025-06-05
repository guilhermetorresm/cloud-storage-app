from dependency_injector import containers, providers

from cloud_storage_app.infrastructure.auth.password_service import PasswordService
from cloud_storage_app.application.services.password_service import PasswordApplicationService
from cloud_storage_app.infrastructure.database.connection import DatabaseManager
from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
from cloud_storage_app.config import get_settings, Settings


class Container(containers.DeclarativeContainer):
    """Container de injeção de dependência."""
    
    # Configurações
    config = providers.Configuration()
    
    # Carrega as configurações do config.py
    settings = providers.Singleton(
        get_settings
    )
    
    # Serviços de Infraestrutura (Singleton)
    database_manager = providers.Singleton(
        DatabaseManager
    )
    
    password_service = providers.Singleton(
        PasswordService
    )
    
    # Repositórios (Factory - nova instância para cada uso)
    user_repository = providers.Factory(
        UserRepository,
        session=database_manager.provided.get_session
    )
    
    # Serviços de Aplicação (Factory)
    password_application_service = providers.Factory(
        PasswordApplicationService,
        password_service=password_service
    )
    
    def init_resources(self) -> None:
        """Inicializa recursos que precisam de setup."""
        # Inicializa o banco de dados
        self.database_manager().initialize()
    
    def shutdown_resources(self) -> None:
        """Limpa recursos ao desligar a aplicação."""
        # Fecha conexões do banco
        self.database_manager().close()
