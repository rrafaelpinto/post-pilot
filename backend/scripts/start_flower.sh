#!/bin/bash

# Script para iniciar o Flower (monitoramento)
echo "Iniciando Flower..."

cd "$(dirname "$0")/.."

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Ambiente virtual ativado"
fi

# Iniciar flower
celery -A post_pilot flower --port=5555
