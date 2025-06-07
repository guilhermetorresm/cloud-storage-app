#!/usr/bin/env python3
"""
Script para configurar e gerenciar o banco de dados e migrações Alembic.
Fornece uma interface unificada para todas as operações de banco de dados.
"""

import asyncio
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional

# Adicionar o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cloud_storage_app.config import get_settings
from cloud_storage_app.infrastructure.database.connection import db_manager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerenciador de operações do banco de dados e Alembic"""
    
    def __init__(self):
        self.settings = get_settings()
        self.alembic_dir = Path("alembic")
        self.alembic_ini = Path("alembic.ini")
    
    def _run_command(self, cmd: list[str], description: str) -> bool:
        """Executa um comando e retorna True se bem-sucedido"""
        try:
            logger.info(f"🔄 {description}...")
            logger.debug(f"Executando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {description} - Sucesso")
                if result.stdout.strip():
                    logger.info(f"Output: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ {description} - Falhou")
                if result.stderr.strip():
                    logger.error(f"Erro: {result.stderr.strip()}")
                if result.stdout.strip():
                    logger.error(f"Output: {result.stdout.strip()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar {description}: {e}")
            return False
    
    async def test_connection(self, max_retries: int = 5, retry_delay: int = 2) -> bool:
        """Testa a conexão com o banco de dados com retry"""
        logger.info("🔍 Testando conexão com o banco de dados...")
        
        for attempt in range(max_retries):
            try:
                # Exibir configurações (sem senha)
                db_url = self.settings.database.get_database_url()
                safe_db_url = db_url.replace(f":{self.settings.database.postgres_password}@", ":***@")
                
                logger.info(f"📋 Tentativa {attempt + 1}/{max_retries}")
                logger.info(f"  • URL: {safe_db_url}")
                logger.info(f"  • Servidor: {self.settings.database.postgres_server}")
                logger.info(f"  • Porta: {self.settings.database.postgres_port}")
                logger.info(f"  • Banco: {self.settings.database.postgres_db}")
                logger.info(f"  • Usuário: {self.settings.database.postgres_user}")
                
                await db_manager.initialize()
                is_healthy = await db_manager.health_check()
                
                if is_healthy:
                    logger.info("✅ Conexão com o banco de dados funcionando!")
                    return True
                else:
                    logger.warning(f"⚠️ Falha na verificação de saúde do banco (tentativa {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        logger.info(f"🔄 Aguardando {retry_delay} segundos antes da próxima tentativa...")
                        await asyncio.sleep(retry_delay)
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao testar conexão (tentativa {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Aguardando {retry_delay} segundos antes da próxima tentativa...")
                    await asyncio.sleep(retry_delay)
            finally:
                try:
                    await db_manager.close()
                except:
                    pass
        
        logger.error("❌ Todas as tentativas de conexão falharam")
        return False
    
    def check_alembic_setup(self) -> bool:
        """Verifica se o Alembic está configurado"""
        if not self.alembic_ini.exists():
            logger.error("❌ Arquivo alembic.ini não encontrado")
            return False
        
        if not self.alembic_dir.exists():
            logger.error("❌ Diretório alembic/ não encontrado")
            return False
        
        # Verificar e criar diretório versions se não existir
        versions_dir = self.alembic_dir / "versions"
        if not versions_dir.exists():
            logger.info("📁 Criando diretório alembic/versions/...")
            versions_dir.mkdir(parents=True, exist_ok=True)
            
            # Criar __init__.py no diretório versions
            init_file = versions_dir / "__init__.py"
            if not init_file.exists():
                with open(init_file, "w") as f:
                    f.write("# Arquivo vazio para tornar este diretório um módulo Python\n")
                logger.info("✅ Criado __init__.py no diretório versions")
            
        logger.info("✅ Alembic está configurado")
        return True
    
    def init_alembic(self) -> bool:
        """Inicializa o Alembic no projeto"""
        if self.check_alembic_setup():
            logger.info("ℹ️ Alembic já está inicializado")
            return True
        
        return self._run_command(
            ["alembic", "init", "alembic"],
            "Inicializando Alembic"
        )
    
    def create_migration(self, message: str = "auto_migration") -> bool:
        """Cria uma nova migração"""
        if not self.check_alembic_setup():
            logger.error("❌ Alembic não está configurado. Execute 'init' primeiro.")
            return False
        
        return self._run_command(
            ["alembic", "revision", "--autogenerate", "-m", message],
            f"Criando migração: {message}"
        )
    
    def upgrade_database(self, revision: str = "head") -> bool:
        """Executa upgrade das migrações"""
        if not self.check_alembic_setup():
            logger.error("❌ Alembic não está configurado. Execute 'init' primeiro.")
            return False
        
        return self._run_command(
            ["alembic", "upgrade", revision],
            f"Executando upgrade para: {revision}"
        )
    
    def downgrade_database(self, revision: str) -> bool:
        """Executa downgrade das migrações"""
        if not self.check_alembic_setup():
            logger.error("❌ Alembic não está configurado. Execute 'init' primeiro.")
            return False
        
        return self._run_command(
            ["alembic", "downgrade", revision],
            f"Executando downgrade para: {revision}"
        )
    
    def show_history(self) -> bool:
        """Mostra o histórico de migrações"""
        if not self.check_alembic_setup():
            logger.error("❌ Alembic não está configurado. Execute 'init' primeiro.")
            return False
        
        return self._run_command(
            ["alembic", "history", "--verbose"],
            "Exibindo histórico de migrações"
        )
    
    def show_current(self) -> bool:
        """Mostra a revisão atual do banco"""
        if not self.check_alembic_setup():
            logger.error("❌ Alembic não está configurado. Execute 'init' primeiro.")
            return False
        
        return self._run_command(
            ["alembic", "current", "--verbose"],
            "Exibindo revisão atual"
        )
    
    def show_heads(self) -> bool:
        """Mostra as revisões head disponíveis"""
        if not self.check_alembic_setup():
            logger.error("❌ Alembic não está configurado. Execute 'init' primeiro.")
            return False
        
        return self._run_command(
            ["alembic", "heads", "--verbose"],
            "Exibindo revisões head"
        )
    
    def stamp_database(self, revision: str = "head") -> bool:
        """Marca o banco com uma revisão específica (sem executar migrações)"""
        if not self.check_alembic_setup():
            logger.error("❌ Alembic não está configurado. Execute 'init' primeiro.")
            return False
        
        return self._run_command(
            ["alembic", "stamp", revision],
            f"Marcando banco com revisão: {revision}"
        )
    
    async def setup_complete(self) -> bool:
        """Executa o setup completo do banco de dados"""
        logger.info("🚀 Iniciando setup completo do banco de dados...")
        
        # 1. Testar conexão
        logger.info("\n📋 Passo 1: Verificando conexão com banco")
        if not await self.test_connection():
            logger.error("❌ Setup falhou: não foi possível conectar ao banco")
            return False
        
        # 2. Inicializar Alembic se necessário
        logger.info("\n📋 Passo 2: Verificando configuração do Alembic")
        if not self.init_alembic():
            logger.error("❌ Setup falhou: não foi possível configurar Alembic")
            return False
        
        # 3. Criar migração inicial se não existir
        logger.info("\n📋 Passo 3: Verificando migrações")
        migrations_dir = self.alembic_dir / "versions"
        if migrations_dir.exists() and list(migrations_dir.glob("*.py")):
            logger.info("ℹ️ Migrações já existem")
        else:
            logger.info("📝 Criando migração inicial...")
            if not self.create_migration("initial_migration"):
                logger.error("❌ Setup falhou: não foi possível criar migração inicial")
                return False
        
        # 4. Executar migrações
        logger.info("\n📋 Passo 4: Executando migrações")
        if not self.upgrade_database():
            logger.error("❌ Setup falhou: não foi possível executar migrações")
            return False
        
        # 5. Verificar status final
        logger.info("\n📋 Passo 5: Verificando status final")
        self.show_current()
        
        logger.info("\n🎉 Setup completo do banco de dados finalizado com sucesso!")
        return True


def print_help():
    """Exibe a ajuda do script"""
    help_text = """
🗄️ Script de Gerenciamento do Banco de Dados

USO:
    python scripts/setup_database.py [COMANDO] [ARGUMENTOS]

COMANDOS DISPONÍVEIS:

📋 Configuração e Setup:
    setup              - Setup completo (conexão + alembic + migrações)
    test               - Testar conexão com o banco de dados
    init               - Inicializar Alembic no projeto

🔄 Migrações:
    revision [MSG]     - Criar nova migração (MSG = mensagem descritiva)
    migrate            - Executar todas as migrações pendentes (upgrade head)
    upgrade [REV]      - Fazer upgrade para revisão específica
    downgrade [REV]    - Fazer downgrade para revisão específica

📊 Informações:
    current            - Mostrar revisão atual do banco
    history            - Mostrar histórico de migrações
    heads              - Mostrar revisões head disponíveis

🔧 Utilitários:
    stamp [REV]        - Marcar banco com revisão (sem executar migração)
    help               - Mostrar esta ajuda

EXEMPLOS:
    python scripts/setup_database.py setup
    python scripts/setup_database.py revision "add users table"
    python scripts/setup_database.py upgrade head
    python scripts/setup_database.py downgrade -1
    python scripts/setup_database.py history

NOTAS:
    - REV pode ser: head, base, hash da revisão, ou número relativo (-1, +1)
    - Use 'base' para downgrade completo
    - Use 'head' para upgrade completo
    """
    print(help_text)


async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    db_mgr = DatabaseManager()
    
    logger.info(f"🎯 Executando comando: {command}")
    logger.info(f"📁 Diretório de trabalho: {Path.cwd()}")
    logger.info(f"🌍 Environment: {db_mgr.settings.app.environment}")
    
    success = True
    
    try:
        if command == "help":
            print_help()
        
        elif command == "setup":
            success = await db_mgr.setup_complete()
        
        elif command == "test":
            success = await db_mgr.test_connection()
        
        elif command == "init":
            success = db_mgr.init_alembic()
        
        elif command == "revision":
            message = sys.argv[2] if len(sys.argv) > 2 else "auto_migration"
            success = db_mgr.create_migration(message)
        
        elif command == "migrate":
            success = db_mgr.upgrade_database()
        
        elif command == "upgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            success = db_mgr.upgrade_database(revision)
        
        elif command == "downgrade":
            if len(sys.argv) < 3:
                logger.error("❌ Comando downgrade requer uma revisão. Ex: downgrade -1")
                success = False
            else:
                revision = sys.argv[2]
                success = db_mgr.downgrade_database(revision)
        
        elif command == "current":
            success = db_mgr.show_current()
        
        elif command == "history":
            success = db_mgr.show_history()
        
        elif command == "heads":
            success = db_mgr.show_heads()
        
        elif command == "stamp":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            success = db_mgr.stamp_database(revision)
        
        else:
            logger.error(f"❌ Comando '{command}' não reconhecido")
            print_help()
            success = False
    
    except KeyboardInterrupt:
        logger.info("\n⏹️ Operação cancelada pelo usuário")
        success = False
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        success = False
    
    if success:
        logger.info("✅ Operação concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Operação falhou!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
