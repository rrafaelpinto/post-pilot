#!/bin/bash

# Script para iniciar o Celery Beat (scheduler)
echo "Iniciando Celery Beat..."

cd "$(dirname "$0")/.."

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Ambiente virtual ativado"
fi

# Iniciar beat do Celery
celery -A post_pilot beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
