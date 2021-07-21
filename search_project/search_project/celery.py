import os

from celery import Celery
from celery_once import QueueOnce
from django.core.cache import cache
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_project.settings')

app = Celery('search_project',
             include=['search_app.tasks'])
app.conf.update(
    result_expired=3600,
)
app.conf.timezone = 'Asia/Seoul'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# @app.task(bind=True, base=QueueOnce)
# def debug_task(self):
#     print(f'Request: {self.request!r}')

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
    print("hello~~")
