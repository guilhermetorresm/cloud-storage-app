#!/usr/bin/env python3
"""
Scripts para configurar e gerenciar o banco de dados
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from infrastructure.database.connection import db_manager
from config import get_settings


async def init_alembic():
    """Inicializa o Alembic no projeto"""
    try:
        # Verificar se alembic já está inicializado
        if Path("alembic").exists():
            print("✓ Alembic já está inicializado")
            return
        
        print("📝 Inicializando Alembic...")
        result = subprocess.run(
            ["alembic", "init", "alembic"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Alembic inicializado com sucesso")
        else:
            print(f"❌ Erro ao inicializar Alembic: {result.stderr}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro ao inicializar Alembic: {e}")
        sys.exit(1)

async def create_first_migration():
    """Cria a primeira migração"""
    try:
        print("📝 Criando migração inicial...")
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "create_users_table"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Migração inicial criada")
            print(result.stdout)
        else:
            print(f"❌ Erro ao criar migração: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erro ao criar migração: {e}")

async def run_migrations():
    """Executa as migrações pendentes"""
    try:
        print("🔄 Executando migrações...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Migrações executadas com sucesso")
            print(result.stdout)
        else:
            print(f"❌ Erro ao executar migrações: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")

async def test_connection():
    """Testa a conexão com o banco"""
    try:
        print("🔍 Testando conexão com banco...")
        await db_manager.initialize()
        
        is_healthy = await db_manager.health_check()
        if is_healthy:
            print("✓ Conexão com banco OK")
        else:
            print("❌ Falha na conexão com banco")
            
        await db_manager.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")

async def setup_database():
    """Setup completo do banco de dados"""
    settings = get_settings()
    print(f"🚀 Configurando banco de dados ({settings.app.environment})")
    print(f"📊 Database URL: {settings.database.get_database_url()}")
    
    # 1. Testar conexão
    await test_connection()
    
    # 2. Inicializar Alembic se necessário
    await init_alembic()
    
    # 3. Criar migração inicial
    await create_first_migration()
    
    # 4. Executar migrações
    await run_migrations()
    
    print("✅ Setup do banco concluído!")

if __name__ == "__main__":
    # Comandos disponíveis
    if len(sys.argv) < 2:
        print("Uso: python setup_database.py [comando]")
        print("Comandos disponíveis:")
        print("  setup     - Setup completo")
        print("  test      - Testar conexão")
        print("  migrate   - Executar migrações")
        print("  revision  - Criar nova migração")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "setup":
        asyncio.run(setup_database())
    elif command == "test":
        asyncio.run(test_connection())
    elif command == "migrate":
        asyncio.run(run_migrations())
    elif command == "revision":
        message = sys.argv[2] if len(sys.argv) > 2 else "auto_migration"
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])
    else:
        print(f"Comando '{command}' não reconhecido")
