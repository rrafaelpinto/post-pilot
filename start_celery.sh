#!/bin/bash

# Script para iniciar Celery Worker

echo "🔄 Iniciando Celery Worker..."
echo "==============================="

cd backend

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "   Execute primeiro: ./start_backend.sh"
    exit 1
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar se Redis está rodando
if ! redis-cli ping >/dev/null 2>&1; then
    echo "❌ Redis não está rodando!"
    echo "   Execute: redis-server"
    echo "   Ou instale: sudo apt install redis-server"
    exit 1
fi

echo "🌐 Iniciando Celery Worker..."
echo "   Flower disponível em: http://localhost:5555"
echo ""
echo "Para parar o worker, pressione Ctrl+C"
echo ""

# Iniciar worker
./scripts/start_worker.sh
