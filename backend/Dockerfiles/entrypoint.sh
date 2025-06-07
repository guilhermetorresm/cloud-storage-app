#!/bin/bash

# Esperar o banco de dados estar pronto
echo "🔄 Aguardando o banco de dados estar pronto..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ Banco de dados está pronto!"

# Executar setup do banco de dados
echo "🔄 Executando setup do banco de dados..."
python scripts/setup_database.py migrate

# Iniciar a aplicação
echo "🚀 Iniciando a aplicação..."
exec uvicorn cloud_storage_app.main:app --reload --host 0.0.0.0 --port 8080 