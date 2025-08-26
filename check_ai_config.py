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


def test_provider_configuration():
    print('🔍 DIAGNÓSTICO COMPLETO - CONFIGURAÇÃO AI PROVIDERS')
    print('=' * 70)
    
    # 1. Verificar variáveis de ambiente do sistema
    print('\n📋 1. VARIÁVEIS DE AMBIENTE DO SISTEMA:')
    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GROK_API_KEY': os.getenv('GROK_API_KEY'), 
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'DEFAULT_AI_PROVIDER': os.getenv('DEFAULT_AI_PROVIDER')
    }
    
    for var, value in env_vars.items():
        if value:
            print(f'   ✅ {var}: {"*" * 10}...{value[-4:]}' if len(value) > 10 else f'   ✅ {var}: {value}')
        else:
            print(f'   ❌ {var}: não configurada')
    
    # 2. Verificar configurações do Django
    print('\n⚙️  2. CONFIGURAÇÕES DO DJANGO SETTINGS:')
    django_settings = {
        'OPENAI_API_KEY': getattr(settings, 'OPENAI_API_KEY', ''),
        'GROK_API_KEY': getattr(settings, 'GROK_API_KEY', ''),
        'GEMINI_API_KEY': getattr(settings, 'GEMINI_API_KEY', ''),
        'DEFAULT_AI_PROVIDER': getattr(settings, 'DEFAULT_AI_PROVIDER', '')
    }
    
    for setting, value in django_settings.items():
        if value:
            display_value = f'{"*" * 10}...{value[-4:]}' if len(value) > 10 and 'API_KEY' in setting else value
            print(f'   ✅ {setting}: {display_value}')
        else:
            print(f'   ❌ {setting}: não configurada')
    
    # 3. Testar criação de cada serviço
    print('\n🧪 3. TESTE DE CRIAÇÃO DOS SERVIÇOS:')
    for provider in ['openai', 'grok', 'gemini']:
        try:
            service = AIServiceFactory.create_service(provider)
            api_key_status = "✅ Configurada" if service.api_key else "❌ Não configurada"
            print(f'   {provider.upper()}: {type(service).__name__} - API Key: {api_key_status}')
            if hasattr(service, 'base_url') and getattr(service, 'base_url', None):
                print(f'      └── Base URL: {getattr(service, "base_url")}')
        except Exception as e:
            print(f'   {provider.upper()}: ❌ ERRO - {e}')
    
    # 4. Testar serviço padrão
    print('\n🎯 4. SERVIÇO PADRÃO ATUAL:')
    try:
        default_service = get_default_ai_service()
        print(f'   Classe: {type(default_service).__name__}')
        print(f'   Modelo: {default_service.model}')
        print(f'   API Key: {"✅ Configurada" if default_service.api_key else "❌ Não configurada"}')
        if hasattr(default_service, 'base_url') and getattr(default_service, 'base_url', None):
            print(f'   Base URL: {getattr(default_service, "base_url")}')
    except Exception as e:
        print(f'   ❌ ERRO: {e}')
    
    # 5. Instruções para mudança
    print('\n🔧 5. COMO TROCAR O PROVEDOR:')
    print('   Opção 1 - Via variável de ambiente:')
    print('     export DEFAULT_AI_PROVIDER=grok')
    print('     export DEFAULT_AI_PROVIDER=gemini')
    print('     export DEFAULT_AI_PROVIDER=openai')
    print('')
    print('   Opção 2 - Via settings.py (descomente a linha):')
    print('     DEFAULT_AI_PROVIDER = "grok"')
    print('     DEFAULT_AI_PROVIDER = "gemini"') 
    print('     DEFAULT_AI_PROVIDER = "openai"')
    print('')
    print('   Depois reinicie: Django server + Celery worker + Celery beat')
    
    # 6. Teste de funcionalidade
    print('\n🚀 6. TESTE DE FUNCIONALIDADE:')
    provider_name = getattr(settings, 'DEFAULT_AI_PROVIDER', 'openai')
    service = get_default_ai_service()
    
    if service.api_key:
        print(f'   ✅ Pronto para usar {provider_name.upper()}!')
        print('   💡 Teste gerando tópicos via interface web')
    else:
        print(f'   ⚠️  {provider_name.upper()} configurado mas sem API key')
        print('   💡 Configure a variável de ambiente correspondente')

if __name__ == "__main__":
    test_provider_configuration()
