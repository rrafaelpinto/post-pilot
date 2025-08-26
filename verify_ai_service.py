#!/usr/bin/env python
import os
import sys

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_pilot.settings')
django.setup()

from core.services import get_default_ai_service

print('🧪 TESTE FINAL: Verificando qual serviço está sendo usado')
print('=' * 60)

service = get_default_ai_service()
print(f'✅ Serviço atual: {type(service).__name__}')
print(f'✅ Modelo: {service.model}')
print(f'✅ API Key configurada: {"Sim" if service.api_key else "Não"}')

if hasattr(service, 'base_url'):
    print(f'✅ Base URL: {service.base_url}')

print('\n🎯 AGORA REINICIE OS SERVIÇOS:')
print('1. Pare o Django server (Ctrl+C)')
print('2. Pare o Celery worker (Ctrl+C)')  
print('3. Pare o Celery beat (Ctrl+C)')
print('')
print('4. Inicie novamente:')
print('   python manage.py runserver')
print('   celery -A post_pilot worker --loglevel=info')
print('   celery -A post_pilot beat --loglevel=info')
print('')
print('📝 Após reiniciar, teste a geração de tópicos via interface web')
print('   e você verá que agora está usando o Grok/Gemini!')
