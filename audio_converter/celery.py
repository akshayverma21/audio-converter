from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audio_converter.settings')

app = Celery('audio_converter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()