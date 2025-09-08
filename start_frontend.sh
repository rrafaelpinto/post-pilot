#!/bin/bash

# Script para iniciar o frontend React

echo "⚛️  Iniciando Frontend React..."
echo "================================"

cd frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do Node.js..."
    npm install
fi

# Iniciar servidor de desenvolvimento
echo "🌐 Iniciando servidor React em http://localhost:3000"
echo ""
echo "Para parar o servidor, pressione Ctrl+C"
echo ""

npm start
