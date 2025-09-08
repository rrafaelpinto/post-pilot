#!/bin/bash

# Script para iniciar o backend Django

echo "🚀 Iniciando Backend Django..."
echo "================================"

cd backend

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "   Execute: python -m venv .venv"
    exit 1
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar se as dependências estão instaladas
if ! python -c "import django" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Aplicar migrações
echo "🔄 Aplicando migrações..."
python manage.py migrate

# Iniciar servidor
echo "🌐 Iniciando servidor Django em http://localhost:8000"
echo "   API disponível em: http://localhost:8000/api/"
echo "   Admin disponível em: http://localhost:8000/admin/"
echo ""
echo "Para parar o servidor, pressione Ctrl+C"
echo ""

python manage.py runserver
