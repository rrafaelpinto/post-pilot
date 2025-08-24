import os
from celery import Celery
from django.conf import settings

# Configurar o Django settings module para o programa 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_pilot.settings')

app = Celery('post_pilot')

# Usar uma string aqui significa que o worker não precisa serializar
# o objeto de configuração para processos filhos.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregar módulos de tarefas de todas as apps Django registradas
app.autodiscover_tasks()

# Configurações adicionais
app.conf.update(
    # Configurações de timezone
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    
    # Configurações de serialização
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Configurações de resultados
    result_expires=3600,  # 1 hora
    
    # Configurações de retry
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Configurações de roteamento
    task_routes={
        'core.tasks.generate_topics_task': {'queue': 'ai_tasks'},
        'core.tasks.generate_post_content_task': {'queue': 'ai_tasks'},
        'core.tasks.improve_post_content_task': {'queue': 'ai_tasks'},
        'core.tasks.regenerate_image_prompt_task': {'queue': 'ai_tasks'},
    },
    
    # Configurações de filas
    task_default_queue='default',
    task_create_missing_queues=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
