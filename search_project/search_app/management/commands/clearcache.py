from datetime import date
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Cleared cache'

    def handle(self, *args, **options):
        cache.clear()
        print(datetime.datetime.now())
        self.stdout.write(self.style.SUCCESS('Cleared cache\n'))