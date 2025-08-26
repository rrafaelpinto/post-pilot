#!/usr/bin/env python
import os
import sys
import django
import requests
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_pilot.settings')
django.setup()

from core.models import Theme

def test_theme_polling():
    """Testa o polling de status de um tema"""
    
    # Pegar um tema existente
    themes = Theme.objects.all()[:1]
    if not themes:
        print("❌ Nenhum tema encontrado para testar")
        return
    
    theme = themes[0]
    print(f"🧪 Testando polling para tema: {theme.title} (ID: {theme.id})")
    
    # URL do status
    url = f"http://localhost:8000/tasks/status/?theme_id={theme.id}"
    
    try:
        response = requests.get(url)
        print(f"📡 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resposta JSON:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Erro HTTP: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor Django não está rodando em localhost:8000")
        print("💡 Inicie o servidor: python manage.py runserver")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def check_server_running():
    """Verifica se o servidor Django está rodando"""
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🔍 TESTE DE POLLING - STATUS DE TEMAS")
    print("=" * 50)
    
    if check_server_running():
        print("✅ Servidor Django está rodando")
        test_theme_polling()
    else:
        print("❌ Servidor Django não está rodando")
        print("💡 Inicie com: python manage.py runserver")
