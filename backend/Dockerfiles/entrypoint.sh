#!/bin/bash
set -e

echo "🚀 Iniciando setup do backend..."

# Executar setup do banco de dados (inclui verificação de conexão e migrações)
echo "🔄 Executando setup do banco de dados..."
python scripts/setup_database.py migrate

# Iniciar a aplicação
echo "🚀 Iniciando a aplicação..."
exec uvicorn cloud_storage_app.main:app --reload --host 0.0.0.0 --port 8080 