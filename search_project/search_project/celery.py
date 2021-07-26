import os
import django
from celery import Celery
from django.conf import settings
from django.core.cache import cache
from celery.schedules import crontab
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_project.settings.dev')
app = Celery('search_project',
            include=['search_app.tasks'],
            )
app.config_from_object(__name__)
app.conf.update(
    result_expired=3600,
)
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

app.conf.beat_schedule = {
    # Executes at sunset in Melbourne
    'please_say_hello': {
        'task': 'tasks.test_task1',
        'schedule': 1.0,
    },
}

@app.task
def today_request_delete():
    count = cache.get('today_request')
    cache.decr('today_request', count)
    # try:
    #     print('캐시 삭제: ', cache.delete('today_request'))
    #     print('캐시 생성: ', cache.set('today_request', 0))
    # except:
    #     return False


@app.task
def say_hello():
    logger.info("hello~")
