from .common import *


DEBUG = True
ALLOWED_HOSTS = ['*']



# Celery
CELERY_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'


# celery setting.
CELERY_CACHE_BACKEND = 'default'

# django setting.
# prod에서 redis 캐시가 안먹여서 memcache로 변경
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }
CACHES = {
    'default': {
        'BACKEND': 'djpymemcache.backend.PyMemcacheCache',
        'LOCATION': [
            '127.0.0.1:11211',
        ],
        'OPTIONS': {
            'no_delay': True,
            'ignore_exc': True,
            'max_pool_size': 4,
            'use_pooling': True,
        }
    },
}

SCHEDULE_MINUTE = 60
SCHEDULE_HOUR = 60 * SCHEDULE_MINUTE
SCHEDULE_DAY = 24 * SCHEDULE_HOUR
SCHEDULE_WEEK = 7 * SCHEDULE_DAY
SCHEDULE_MONTH = 30 * SCHEDULE_DAY
# CELERY_BEAT_SCHEDULE = {
#     'today_request_delete': {
#         'task': 'app.tasks.today_request_delete',
#         'schedule': 10.0
#         # 'schedule': 2.0,
#         # 'args': (4, 4)
#     },
#     # 'today_request_delete': {
#     #     'task': 'app.tasks.today_request_delete',
#     #     'schedule': crontab(hour='0',
#     #                         minute=0),
#     #     # 'schedule': 2.0,
#     #     # 'args': (4, 4)
#     # }
#     'say_hello': {
#         'task': 'app.tasks.say_hello',
#         'schedule': 10.0
#         # 'schedule': 2.0,
#         # 'args': (4, 4)
#     },
# }test_task1
# CELERY_BEAT_SCHEDULE = {
#     'say_hello': {
#         'task': 'app.tasks.say_hello',
#         'schedule': 1.0
#         # 'schedule': 2.0,
#         # 'args': (4, 4)
#     },
#     'test_task': {
#         'task': 'app.tasks.test_task1',
#         'schedule': 1.0
#         # 'schedule': 2.0,
#         # 'args': (4, 4)
#     },
# }
