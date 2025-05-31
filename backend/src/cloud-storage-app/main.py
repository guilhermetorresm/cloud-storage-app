import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from .config import get_settings
from .infrastructure.database.connection import init_database, close_database
from .presentation.api.v1 import auth, files, users, health
from .presentation.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from .shared.exceptions import CloudStorageException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Carregar configurações
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Context manager para gerenciar o ciclo de vida da aplicação.
    Executa código no startup e shutdown.
    """
    # Startup
    logger.info("Starting Cloud Storage API...")
    
    try:
        # Inicializar banco de dados
        await init_database()
        logger.info("Database initialized successfully")
        
        # Outras inicializações podem ser adicionadas aqui
        # Ex: inicializar cache Redis, conectar com S3, etc.
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    # Aplicação está rodando
    yield
    
    # Shutdown
    logger.info("Shutting down Cloud Storage API...")
    
    try:
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


# Incluir routers da API
api_prefix = "/api/v1"

app.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"]
)

app.include_router(
    auth.router,
    prefix=f"{api_prefix}/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix=f"{api_prefix}/users",
    tags=["Users"]
)

app.include_router(
    files.router,
    prefix=f"{api_prefix}/files",
    tags=["Files"]
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