import os
import django
from celery import Celery
from django.conf import settings
from django.core.cache import cache
from celery.schedules import crontab
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_project.settings.prod')
app = Celery('search_project',
            include=['search_app.tasks'],
            )
app.config_from_object(__name__)
# app.conf.update(
#     result_expired=0,
# )
app.conf.timezone = 'Asia/Seoul'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# @app.task(bind=True, base=QueueOnce)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Seoul',
    CELERY_ENABLE_UTC=False,
    CELERY_BEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
)
django.setup()