"""
Router para health checks da aplicação.
Verifica o status dos serviços essenciais.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_database_session, db_manager
from ....config import get_settings


logger = logging.getLogger(__name__)
router = APIRouter()

settings = get_settings()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check básico da aplicação.
    Retorna status simples sem verificações profundas.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.app.app_name,
        "version": settings.app.app_version
    }


@router.get("/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check(
    db: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Health check detalhado com verificação de dependências.
    Verifica banco de dados e outros serviços críticos.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.app.app_name,
        "version": settings.app.app_version,
        "environment": settings.app.environment,
        "checks": {}
    }
    
    overall_healthy = True
    
    # Verificar banco de dados
    try:
        db_healthy = await db_manager.health_check()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "message": "Database connection successful" if db_healthy else "Database connection failed"
        }
        if not db_healthy:
            overall_healthy = False
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database check error: {str(e)}"
        }
        overall_healthy = False
    
    # Verificar configurações críticas
    config_issues = []
    
    if not settings.auth.secret_key or settings.auth.secret_key == "your-super-secret-key-change-this-in-production-and-make-it-very-long":
        config_issues.append("SECRET_KEY not properly configured")
    
    if not settings.storage.s3_bucket_name:
        config_issues.append("S3_BUCKET_NAME not configured")
    
    health_status["checks"]["configuration"] = {
        "status": "healthy" if not config_issues else "warning",
        "issues": config_issues if config_issues else None
    }
    
    # Status geral
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    elif config_issues:
        health_status["status"] = "degraded"
    
    # Retornar status HTTP apropriado
    if health_status["status"] == "unhealthy":
        return health_status, status.HTTP_503_SERVICE_UNAVAILABLE
    elif health_status["status"] == "degraded":
        return health_status, status.HTTP_200_OK
    else:
        return health_status


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(
    db: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Readiness probe - verifica se a aplicação está pronta para receber tráfego.
    Usado principalmente em ambientes Kubernetes.
    """
    try:
        # Verificar conexão com banco
        db_healthy = await db_manager.health_check()
        
        if not db_healthy:
            return {
                "status": "not_ready",
                "message": "Database not available"
            }, status.HTTP_503_SERVICE_UNAVAILABLE
        
        return {
            "status": "ready",
            "message": "Application is ready to serve traffic"
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "message": f"Readiness check failed: {str(e)}"
        }, status.HTTP_503_SERVICE_UNAVAILABLE


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness probe - verifica se a aplicação está rodando.
    Usado principalmente em ambientes Kubernetes.
    """
    return {
        "status": "alive",
        "message": "Application is running"
    }