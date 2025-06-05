import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from cloud_storage_app.config import get_settings
from cloud_storage_app.infrastructure.database.connection import init_database, close_database
from cloud_storage_app.infrastructure.di.conteiner import Container
from cloud_storage_app.presentation.api.v1 import health
from cloud_storage_app.presentation.api.v1 import auth
from cloud_storage_app.presentation.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from cloud_storage_app.shared.exceptions import CloudStorageException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Carregar configurações
settings = get_settings()

# Criar container de injeção de dependência
container = Container()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Context manager para gerenciar o ciclo de vida da aplicação.
    Executa código no startup e shutdown.
    """
    # Startup
    logger.info("Starting Cloud Storage API...")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Debug mode: {settings.app.debug}")
    
    try:
        # Inicializar recursos do container
        container.init_resources()
        logger.info("Container resources initialized")
        
        # Inicializar banco de dados
        await init_database()
        logger.info("Database connection initialized")
        
        # Fazer verificação real da conexão
        from cloud_storage_app.infrastructure.database.connection import db_manager
        
        logger.info("Testing database connection...")
        is_healthy = await db_manager.health_check()
        
        if is_healthy:
            logger.info("✅ Database connection test successful")
        else:
            logger.error("❌ Database connection test failed")
            raise RuntimeError("Database connection test failed during startup")
        
        # Configurar wiring do container
        container.wire(modules=[
            "cloud_storage_app.presentation.api.v1.auth",
            "cloud_storage_app.presentation.api.v1.health"
        ])
        logger.info("Container wiring configured")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        
        # Log detalhado das configurações para debug
        logger.error("Current database configuration:")
        logger.error(f"  - POSTGRES_SERVER: {settings.database.postgres_server}")
        logger.error(f"  - POSTGRES_PORT: {settings.database.postgres_port}")
        logger.error(f"  - POSTGRES_DB: {settings.database.postgres_db}")
        logger.error(f"  - POSTGRES_USER: {settings.database.postgres_user}")
        logger.error(f"  - DATABASE_URL configured: {settings.database.database_url is not None}")
        
        raise
    
    # Aplicação está rodando
    yield
    
    # Shutdown
    logger.info("Shutting down Cloud Storage API...")
    
    try:
        # Limpar recursos do container
        container.shutdown_resources()
        logger.info("Container resources cleaned up")
        
        # Fechar conexões do banco
        await close_database()
        logger.info("Database connections closed")
        
        # Outras limpezas podem ser adicionadas aqui
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app.app_name,
    description="API para armazenamento de arquivos em nuvem",
    version=settings.app.app_version,
    debug=settings.app.debug,
    lifespan=lifespan,
    # Configurações de documentação
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
    openapi_url="/openapi.json" if settings.app.debug else None,
)

# Adicionar container à aplicação
app.container = container

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# Registrar exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(CloudStorageException, general_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Middleware para logging de requests (apenas em debug)
if settings.app.debug:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição
        logger.info(f"Request: {request.method} {request.url}")
        
        # Processar requisição
        response = await call_next(request)
        
        # Log da resposta
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        return response


app.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)


# Endpoint raiz
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Cloud Storage API",
        "version": settings.app.app_version,
        "status": "running",
        "docs": "/docs" if settings.app.debug else "disabled"
    }


# Endpoint de informações da API
@app.get("/info", status_code=status.HTTP_200_OK)
async def api_info():
    """Informações sobre a API"""
    return {
        "name": settings.app.app_name,
        "version": settings.app.app_version,
        "environment": settings.app.environment,
        "debug": settings.app.debug,
    }


if __name__ == "__main__":
    import uvicorn
    import time
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app.debug,
        log_level="info" if not settings.app.debug else "debug"
    )