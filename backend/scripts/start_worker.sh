#!/bin/bash

# Script para iniciar o worker do Celery
echo "Iniciando Celery Worker..."

cd "$(dirname "$0")/.."

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Ambiente virtual ativado"
fi

# Iniciar worker do Celery
celery -A post_pilot worker --loglevel=info --concurrency=2 --queues=default,ai_tasks
