#!/usr/bin/env python
"""
Script para testar a funcionalidade de auto-refresh da página theme_detail.
"""
import os
import sys
import django
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_pilot.settings')
django.setup()

from core.models import Theme
from core.tasks import generate_topic_suggestions_task

def test_auto_refresh():
    """Testa se o auto-refresh funciona após gerar tópicos"""
    
    # Pegar primeiro tema
    theme = Theme.objects.first()
    if not theme:
        print("❌ Nenhum tema encontrado")
        return
        
    print(f"🧪 Testando auto-refresh para tema: {theme.title}")
    print(f"📊 Estado inicial:")
    print(f"   - is_processing: {theme.is_processing}")
    print(f"   - topics_count: {len(theme.suggested_topics.get('topics', [])) if theme.suggested_topics else 0}")
    
    # Simular clique no botão "Gerar Tópicos"
    print(f"\n🚀 Iniciando geração de tópicos...")
    
    # Executar task de forma síncrona para teste
    try:
        result = generate_topic_suggestions_task(theme.id)
        print(f"✅ Task concluída: {result}")
        
        # Verificar estado final
        theme.refresh_from_db()
        print(f"\n📊 Estado final:")
        print(f"   - is_processing: {theme.is_processing}")
        print(f"   - topics_count: {len(theme.suggested_topics.get('topics', [])) if theme.suggested_topics else 0}")
        
        print(f"\n🎯 Teste do endpoint /tasks/status/:")
        import requests
        try:
            response = requests.get(f"http://127.0.0.1:8000/tasks/status/?theme_id={theme.id}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data}")
            else:
                print(f"   ❌ Erro HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro na requisição: {e}")
            
    except Exception as e:
        print(f"❌ Erro na task: {e}")

if __name__ == "__main__":
    print("🔍 TESTE AUTO-REFRESH THEME_DETAIL")
    print("=" * 50)
    test_auto_refresh()
