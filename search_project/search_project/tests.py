import os
from django.core.cache import cache
from django.test import TestCase
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    print(cache.get_or_set('today_request', 124124))


class CacheTests(TestCase):

    def cache_is_working(self):
        cache.get_or_set('test_cache', 1, None)
        self.assertIs(cache.get('test_cache'), 1)

    
        
