import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_project.settings')

app = Celery('search_project',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['search_app.tasks'])

app.conf.update(
    result_expired=3600,
)
app.conf.timezone = 'Asia/Seoul'
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    i = app.control.inspect()
    i.scheduled()
    i.active()
    i.reserved()
    print(f'Request: {self.request!r}')