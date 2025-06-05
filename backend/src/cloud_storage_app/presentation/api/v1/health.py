"""
Router para health checks da aplicação.
Verifica o status dos serviços essenciais.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Tuple

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from ....config import get_settings, AppSettings
from ....infrastructure.di.container import Container


logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# --- Funções de Verificação Modulares ---

@inject
async def check_database(
    db_manager = Depends(Provide[Container.database_manager])
) -> Tuple[str, Dict[str, Any]]:
    """Verifica a conectividade com o banco de dados."""
    try:
        is_healthy = await db_manager.health_check()
        if is_healthy:
            return "healthy", {"status": "healthy", "message": "Database connection successful"}
        else:
            return "unhealthy", {"status": "unhealthy", "message": "Database connection failed"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return "unhealthy", {"status": "unhealthy", "message": f"Database check error: {str(e)}"}

@inject
async def check_critical_configurations(
    settings: AppSettings = Depends(Provide[Container.settings])
) -> Tuple[str, Dict[str, Any]]:
    """Verifica se configurações críticas estão definidas corretamente."""
    issues = []
    
    # Exemplo: Chave secreta não deve ser o valor padrão
    if not settings.auth.secret_key or settings.auth.secret_key == "your-super-secret-key-change-this-in-production-and-make-it-very-long":
        issues.append("AUTH_SECRET_KEY is not properly configured.")
    
    # Exemplo: Nome do bucket S3 deve estar presente
    if not settings.storage.s3_bucket_name:
        issues.append("S3_BUCKET_NAME is not configured.")
        
    if issues:
        # Consideramos um problema de configuração como 'degraded', não 'unhealthy'
        return "degraded", {"status": "degraded", "issues": issues}
    
    return "healthy", {"status": "healthy", "message": "Critical configurations are set."}


# --- Endpoints ---

@router.get("/", status_code=status.HTTP_200_OK, tags=["Health"])
@inject
async def health_check(
    settings: AppSettings = Depends(Provide[Container.settings])
) -> Dict[str, Any]:
    """Health check básico que apenas confirma que a aplicação está online."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.app.app_name,
        "version": settings.app.app_version
    }


@router.get("/detailed", status_code=status.HTTP_200_OK, tags=["Health"])
@inject
async def detailed_health_check(
    settings: AppSettings = Depends(Provide[Container.settings])
) -> JSONResponse:
    """
    Executa um health check detalhado, verificando todas as dependências críticas
    como banco de dados e configurações.
    """
    # Lista de verificações a serem executadas concorrentemente
    checks_to_run = [
        check_database(),
        check_critical_configurations()
    ]
    
    # Executa todas as verificações em paralelo
    results = await asyncio.gather(*checks_to_run)
    
    # Mapeia os nomes das verificações aos resultados
    check_results = {
        "database": results[0][1],
        "configuration": results[1][1]
    }
    
    # Determina o status geral
    overall_status = "healthy"
    for status_result, _ in results:
        if status_result == "unhealthy":
            overall_status = "unhealthy"
            break
        if status_result == "degraded":
            overall_status = "degraded"

    response_body = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.app.app_name,
        "version": settings.app.app_version,
        "environment": settings.app.environment,
        "checks": check_results
    }
    
    # Retorna 503 apenas se um componente crítico estiver indisponível
    if overall_status == "unhealthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response_body
        )
        
    return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)


@router.get("/readiness", status_code=status.HTTP_200_OK, tags=["Health"])
@inject
async def readiness_check() -> JSONResponse:
    """
    Verifica se a aplicação está pronta para receber tráfego (Readiness Probe).
    Falha se dependências essenciais, como o banco de dados, não estiverem prontas.
    """
    db_status, db_details = await check_database()
    
    if db_status != "healthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "details": db_details}
        )
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ready", "message": "Application is ready to serve traffic."}
    )


@router.get("/liveness", status_code=status.HTTP_200_OK, tags=["Health"])
async def liveness_check() -> Dict[str, str]:
    """
    Verifica se a aplicação está rodando (Liveness Probe).
    Deve ser uma checagem rápida e sem dependências externas.
    """
    return {"status": "alive"}