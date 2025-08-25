#!/usr/bin/env python
"""
Script de teste para validar o sistema multi-AI provider
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_pilot.settings')
django.setup()

from core.services import AIServiceFactory, get_default_ai_service
from core.models import Theme
from django.contrib.auth.models import User


def test_ai_providers():
    """Testa todos os provedores de AI disponíveis"""
    print("🧪 Testando Sistema Multi-AI Provider")
    print("=" * 50)
    
    # 1. Testar factory
    print("\n1. Testando AIServiceFactory:")
    providers = AIServiceFactory.get_available_providers()
    print(f"   Provedores disponíveis: {providers}")
    
    # 2. Testar criação de serviços
    print("\n2. Testando criação de serviços:")
    for provider in providers:
        try:
            service = AIServiceFactory.create_service(provider)
            print(f"   ✓ {provider}: {type(service).__name__}")
        except Exception as e:
            print(f"   ✗ {provider}: Erro - {e}")
    
    # 3. Testar serviço padrão
    print("\n3. Testando serviço padrão:")
    try:
        default_service = get_default_ai_service()
        print(f"   ✓ Serviço padrão: {type(default_service).__name__}")
    except Exception as e:
        print(f"   ✗ Erro no serviço padrão: {e}")
        return False
    
    # 4. Testar geração de tópicos (apenas se OpenAI estiver configurado)
    print("\n4. Testando geração de tópicos:")
    try:
        if hasattr(default_service, 'api_key') and default_service.api_key:
            result = default_service.generate_topics("Python Testing", [])
            if result and result.get('topics'):
                print(f"   ✓ Gerados {len(result['topics'])} tópicos")
                for i, topic in enumerate(result['topics'][:2], 1):
                    print(f"      {i}. {topic.get('title', 'Sem título')}")
            else:
                print("   ⚠ Nenhum tópico gerado")
        else:
            print("   ⚠ API key não configurada - pulando teste de geração")
    except Exception as e:
        print(f"   ✗ Erro na geração de tópicos: {e}")
    
    # 5. Testar integração com tasks
    print("\n5. Testando integração com tasks:")
    try:
        from core.tasks import generate_topics_task
        print("   ✓ Tasks importadas com sucesso")
        
        # Verificar se existe um tema para testar
        if Theme.objects.exists():
            theme = Theme.objects.first()
            print(f"   ✓ Tema encontrado para teste: {theme.title}")
        else:
            print("   ⚠ Nenhum tema encontrado - criando tema de teste")
            user = User.objects.first()
            if user:
                theme = Theme.objects.create(
                    title="Python Testing",
                    description="Tema para testes do sistema multi-AI",
                    created_by=user
                )
                print(f"   ✓ Tema de teste criado: {theme.title}")
            else:
                print("   ⚠ Nenhum usuário encontrado - não é possível criar tema")
    except Exception as e:
        print(f"   ✗ Erro na integração com tasks: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Teste concluído!")
    return True


def test_provider_switching():
    """Testa a troca entre provedores"""
    print("\n🔄 Testando troca de provedores:")
    print("-" * 30)
    
    providers = AIServiceFactory.get_available_providers()
    
    for provider in providers:
        print(f"\n   Testando {provider}:")
        try:
            service = AIServiceFactory.create_service(provider)
            print(f"     ✓ Serviço criado: {type(service).__name__}")
            
            # Verificar se tem API key configurada
            if hasattr(service, 'api_key') and service.api_key:
                print(f"     ✓ API key configurada")
            else:
                print(f"     ⚠ API key não configurada")
                
        except Exception as e:
            print(f"     ✗ Erro: {e}")


def show_configuration():
    """Mostra a configuração atual"""
    print("\n⚙️ Configuração atual:")
    print("-" * 20)
    
    from django.conf import settings
    
    default_provider = getattr(settings, 'DEFAULT_AI_PROVIDER', 'openai')
    print(f"   Provedor padrão: {default_provider}")
    
    # Verificar chaves de API
    api_keys = {
        'OpenAI': getattr(settings, 'OPENAI_API_KEY', ''),
        'Grok': getattr(settings, 'GROK_API_KEY', ''),
        'Gemini': getattr(settings, 'GEMINI_API_KEY', '')
    }
    
    print("   Chaves de API:")
    for provider, key in api_keys.items():
        status = "✓ Configurada" if key else "✗ Não configurada"
        print(f"     {provider}: {status}")


if __name__ == "__main__":
    show_configuration()
    test_ai_providers()
    test_provider_switching()
    
    print("\n📝 Próximos passos:")
    print("   1. Configure as chaves de API dos provedores desejados no .env")
    print("   2. Use 'python manage.py ai_provider --set <provider>' para trocar")
    print("   3. Teste a geração de conteúdo via interface web")
    print("   4. Monitore os logs das tasks do Celery")
