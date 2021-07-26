from .common import *

DEBUG = False
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = [
    "*",
]
CHARSET = 'utf8'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'project3postgres.ceej7pcmvlvh.ap-northeast-2.rds.amazonaws.com',
        'PORT': '5432',
        'NAME': get_secret("DB_NAME"),
        'USER': get_secret("DB_USER"),
        'PASSWORD': get_secret("DB_PASSWORD"),
    }
}
# Celery
CELERY_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'


# celery setting.
CELERY_CACHE_BACKEND = 'default'

# django setting.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'djpymemcache.backend.PyMemcacheCache',
#         'LOCATION': [
#             'host.docker.internal:11211',
#         ],
#         'OPTIONS': {
#             'no_delay': True,
#             'ignore_exc': True,
#             'max_pool_size': 4,
#             'use_pooling': True,
#         }
#     },
# }

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

AWS_REGION = 'ap-northeast-2'
AWS_STORAGE_BUCKET_NAME = 'kang-project3-s3'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (
    AWS_STORAGE_BUCKET_NAME, AWS_REGION)

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False
# Static Setting
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# Media Setting
MEDIA_URL = "https://%s/media/" % AWS_S3_CUSTOM_DOMAIN
DEFAULT_FILE_STORAGE = 'CustomS3Boto3Storage.CustomS3Boto3Storage'


AWS_ACCESS_KEY_ID = get_secret("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_secret("AWS_SECRET_ACCESS_KEY")


AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_LOCATION = 'static'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
