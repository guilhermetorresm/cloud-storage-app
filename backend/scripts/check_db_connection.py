#!/usr/bin/env python3
"""
Script para verificar a conectividade com o banco de dados.
Útil para diagnosticar problemas de conexão.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Adicionar o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cloud_storage_app.config import get_settings
from cloud_storage_app.infrastructure.database.connection import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def check_database_connection():
    """Verifica a conectividade com o banco de dados"""
    
    logger.info("🔍 Iniciando verificação da conexão com o banco de dados...")
    
    # Carregar configurações
    settings = get_settings()
    
    # Exibir configurações (sem senha)
    db_url = settings.database.get_database_url()
    safe_db_url = db_url.replace(f":{settings.database.postgres_password}@", ":***@")
    
    logger.info("📋 Configurações do banco de dados:")
    logger.info(f"  • URL: {safe_db_url}")
    logger.info(f"  • Servidor: {settings.database.postgres_server}")
    logger.info(f"  • Porta: {settings.database.postgres_port}")
    logger.info(f"  • Banco: {settings.database.postgres_db}")
    logger.info(f"  • Usuário: {settings.database.postgres_user}")
    logger.info(f"  • Environment: {settings.app.environment}")
    
    # Inicializar gerenciador de banco
    db_manager = DatabaseManager()
    
    try:
        logger.info("🔌 Tentando inicializar conexão...")
        await db_manager.initialize()
        logger.info("✅ Conexão inicializada com sucesso")
        
        logger.info("🩺 Testando health check...")
        is_healthy = await db_manager.health_check()
        
        if is_healthy:
            logger.info("✅ Health check passou - Banco de dados está funcionando!")
            return True
        else:
            logger.error("❌ Health check falhou - Banco não está respondendo")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        
        # Sugerir soluções baseadas no tipo de erro
        error_msg = str(e).lower()
        
        if "connection refused" in error_msg:
            logger.error("💡 Possíveis soluções:")
            logger.error("   1. Verifique se o PostgreSQL está rodando")
            logger.error("   2. Verifique se a porta está correta")
            logger.error("   3. Se usando Docker, verifique se o container está up")
            
        elif "authentication failed" in error_msg or "password" in error_msg:
            logger.error("💡 Possíveis soluções:")
            logger.error("   1. Verifique o usuário e senha")
            logger.error("   2. Verifique as variáveis de ambiente")
            
        elif "database" in error_msg and "does not exist" in error_msg:
            logger.error("💡 Possíveis soluções:")
            logger.error("   1. Crie o banco de dados")
            logger.error("   2. Verifique o nome do banco nas configurações")
            
        elif "host" in error_msg or "resolve" in error_msg:
            logger.error("💡 Possíveis soluções:")
            logger.error("   1. Verifique o hostname/IP do servidor")
            logger.error("   2. Verifique a conectividade de rede")
            
        return False
        
    finally:
        try:
            await db_manager.close()
            logger.info("🔒 Conexões fechadas")
        except Exception as e:
            logger.warning(f"Aviso ao fechar conexões: {e}")


async def check_environment():
    """Verifica se as variáveis de ambiente estão configuradas"""
    
    logger.info("🌍 Verificando variáveis de ambiente...")
    
    import os
    
    required_vars = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD", 
        "POSTGRES_DB",
        "POSTGRES_SERVER",
        "POSTGRES_PORT"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        else:
            logger.info(f"  ✅ {var}: {value if var != 'POSTGRES_PASSWORD' else '***'}")
    
    if missing_vars:
        logger.error(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        logger.error("💡 Crie um arquivo .env no diretório backend/ com:")
        for var in missing_vars:
            if var == "POSTGRES_PASSWORD":
                logger.error(f"   {var}=sua_senha_aqui")
            elif var == "POSTGRES_USER":
                logger.error(f"   {var}=postgres")
            elif var == "POSTGRES_DB":
                logger.error(f"   {var}=cloud_storage_db")
            elif var == "POSTGRES_SERVER":
                logger.error(f"   {var}=localhost")  # ou 'db' se usando Docker
            elif var == "POSTGRES_PORT":
                logger.error(f"   {var}=5432")
        return False
    
    logger.info("✅ Todas as variáveis de ambiente estão configuradas")
    return True


async def main():
    """Função principal"""
    logger.info("🚀 Iniciando diagnóstico do banco de dados...")
    
    # Verificar variáveis de ambiente
    env_ok = await check_environment()
    
    if not env_ok:
        logger.error("❌ Configuração incompleta. Corrija e tente novamente.")
        return False
    
    # Verificar conexão
    db_ok = await check_database_connection()
    
    if db_ok:
        logger.info("🎉 Tudo funcionando perfeitamente!")
        return True
    else:
        logger.error("❌ Problemas encontrados na conexão")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 