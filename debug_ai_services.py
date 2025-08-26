#!/usr/bin/env python
import os
import sys

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_pilot.settings')
django.setup()

from django.conf import settings

from core.services import AIServiceFactory, get_default_ai_service

print('=== DIAGNÓSTICO DO PROBLEMA ===')
print(f'DEFAULT_AI_PROVIDER no settings: {getattr(settings, "DEFAULT_AI_PROVIDER", "NÃO DEFINIDO")}')
print(f'OPENAI_API_KEY: {"✓ Definida" if getattr(settings, "OPENAI_API_KEY", "") else "✗ Não definida"}')
print(f'GROK_API_KEY: {"✓ Definida" if getattr(settings, "GROK_API_KEY", "") else "✗ Não definida"}')
print(f'GEMINI_API_KEY: {"✓ Definida" if getattr(settings, "GEMINI_API_KEY", "") else "✗ Não definida"}')

print('\n=== TESTE DE CRIAÇÃO DE SERVIÇOS ===')

# Teste direto com factory
for provider in ['openai', 'grok', 'gemini']:
    try:
        service = AIServiceFactory.create_service(provider)
        print(f'{provider}: {type(service).__name__} - API Key: {"✓" if service.api_key else "✗"}')
    except Exception as e:
        print(f'{provider}: ERRO - {e}')

print('\n=== TESTE DO SERVIÇO PADRÃO ===')
default_service = get_default_ai_service()
print(f'Serviço padrão retornado: {type(default_service).__name__}')
print(f'API Key do serviço padrão: {"✓ Configurada" if default_service.api_key else "✗ Não configurada"}')

print('\n=== TESTE DE MUDANÇA DE PROVEDOR ===')
# Teste mudando via env variable
for provider in ['grok', 'gemini', 'openai']:
    os.environ['DEFAULT_AI_PROVIDER'] = provider
    # Reload settings
    from importlib import reload

    import post_pilot.settings
    reload(post_pilot.settings)
    
    service = get_default_ai_service()
    print(f'Env={provider} -> {type(service).__name__}')
