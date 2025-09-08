# Isso garante que o app sempre seja importado quando o Django iniciar
# para que shared_task use esta app.
from .celery import app as celery_app

__all__ = ('celery_app',)