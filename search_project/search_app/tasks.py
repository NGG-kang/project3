from pprint import pformat
from celery.events.snapshot import Polaroid
import time
from datetime import datetime, timedelta
import celery
from django.utils import timezone
from celery import shared_task

from celery.utils.log import get_task_logger
from contextlib import contextmanager
from django.core.cache import cache
from hashlib import md5

import requests

from search_app.models import CrwalingModel, SaraminInfo, JobKoreaInfo, JobPlanetInfo, KreditJobInfo, CrwalingPhotos
from search_project.celery import app
from search_app.crawling.saramin import GetSaraminEnterInfo
from search_app.crawling.jobkorea import GetJobKoreaInfo
from search_app.crawling.jobplanet import GetJobPlanetInfo
from search_app.crawling.kreditjob import GetKreditJobInfo
from search_app.search import SearchJob
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from celery_once import QueueOnce
from kombu import Queue

# worker수 제한
# 이름을 넣고, 이름에 맞는 celery를 worker 1 로두고 시작한다
app.conf.task_queues = (
    Queue('crwaling_enter_info', routing_key='crwaling.#'),
    Queue('today_request_delete', routing_key='today.#'),
)


logger = get_task_logger(__name__)

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes

@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)



@shared_task(bind=True, retry=False)
def crwaling_enter_info(self, company_name, url):
    print(company_name, '중복 체크 시작')

    company_name_unicode = company_name.encode(encoding='utf-8')
    company_name_hexdigest = md5(company_name_unicode).hexdigest()
    lock_id = '{0}-lock-{1}'.format(self.name, company_name_hexdigest)
    logger.debug('Importing feed: %s', company_name)
    # 이미 동일한 네임이 들어가있으면 그냥 넘어감
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            print(company_name, url)
            print("task start")
            # i = app.control.inspect()
            # print(i.scheduled())
            # print(i.active())
            # print(i.reserved())
            company_name = company_name.replace(' ', '').replace(
                '\n', '').lstrip('(주)').rstrip('(주)').strip().split('(')[0]
            # 테스트용
            # saramin = GetSaraminEnterInfo()
            # saramin_location = saramin.get_company_info(url)
            # jobkorea = GetJobKoreaInfo()
            # jobkorea_location = jobkorea.get_company_info(company_name=company_name)
            # jobplanet = GetJobPlanetInfo()
            # jobplanet_location = jobplanet.get_company_info(company_name=company_name)
            # kreditjob = GetKreditJobInfo()
            # kreditjob.get_company_info(company_name=company_name, saramin_location=saramin_location, jobkorea_location=jobkorea_location, jobplanet_location=jobplanet_location)

            # 실사용 코드
            # DB에 저장되어서 다시 불러온것도 가능함
            # DB에서 빈값을 불러와도 정상적으로 작동
            object = CrwalingModel.objects.filter(enter_name=company_name).first()
            if object:
                time_cal = object.created_at+timedelta(days=0)
                now = timezone.now()
                print("생성된날", object.created_at)
                print("생성된날 + 7일", time_cal)
                print("오늘", now)
                if time_cal <= now:
                    print("7일 이상 지났습니다.")
                    saramin = SaraminInfo.objects.get(enter=object)
                    jobkorea = JobKoreaInfo.objects.get(enter=object)
                    jobplanet = JobPlanetInfo.objects.get(enter=object)
                    kreditjob = KreditJobInfo.objects.get(enter=object)
                    saramin_company_name = saramin.enter.enter_name
                    if saramin_company_name:
                        company_name = saramin_company_name
                    saramin = GetSaraminEnterInfo(
                        company_csn=saramin.company_code, company_name=company_name, company_url=saramin.url)
                    enter, saramin_location = saramin.get_company_info(
                        url, company_name)

                    jobkorea = GetJobKoreaInfo(enter=enter, company_url=jobkorea.url)
                    jobkorea_location = jobkorea.get_company_info(
                        company_name=company_name)

                    jobplanet = GetJobPlanetInfo(
                        enter=enter, company_url=jobplanet.url)
                    jobplanet_location = jobplanet.get_company_info(
                        company_name=company_name)

                    kreditjob = GetKreditJobInfo(
                        enter=enter, company_url=kreditjob.url)
                    kreditjob.get_company_info(company_name=company_name, saramin_location=saramin_location,
                                            jobkorea_location=jobkorea_location, jobplanet_location=jobplanet_location)
                else:
                    print("7일이 지나지 않았습니다. 7일이 지난 후에 신청하세요")
                    raise Exception
            else:
                saramin = GetSaraminEnterInfo()
                enter, saramin_location = saramin.get_company_info(
                    saramin_url=url, company_name=company_name)

                jobkorea = GetJobKoreaInfo(enter=enter)
                jobkorea_location = jobkorea.get_company_info(
                    company_name=company_name)
                jobplanet = GetJobPlanetInfo(enter=enter)
                jobplanet_location = jobplanet.get_company_info(
                    company_name=company_name)
                kreditjob = GetKreditJobInfo(enter=enter)
                kreditjob.get_company_info(company_name=company_name, saramin_location=saramin_location,
                                        jobkorea_location=jobkorea_location, jobplanet_location=jobplanet_location)

            # 끝났으면 오늘 요청건수 1회 늘림
            cache.incr('today_request')
        else:
            logger.debug(
                '%s is already being imported by another worker', company_name)


class DumpCam(Polaroid):
    clear_after = True  # clear after flush (incl, state.event_count).

    def on_shutter(self, state):
        if not state.event_count:
            # No new events since last snapshot.
            return
        print('Workers: {0}'.format(pformat(state.workers, indent=4)))
        print('Tasks: {0}'.format(pformat(state.tasks, indent=4)))
        print('Total: {0.event_count} events, {0.task_count} tasks'.format(
            state))
