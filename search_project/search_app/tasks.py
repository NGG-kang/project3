from datetime import datetime, timedelta
from django.utils import timezone
from celery import shared_task

from search_app.models import CrwalingModel, SaraminInfo, JobKoreaInfo, JobPlanetInfo, KreditJobInfo, CrwalingPhotos
from search_project.celery import app
from search_app.crawling.saramin import GetSaraminEnterInfo
from search_app.crawling.jobkorea import GetJobKoreaInfo
from search_app.crawling.jobplanet import GetJobPlanetInfo
from search_app.crawling.kreditjob import GetKreditJobInfo
from search_app.search import SearchJob
from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
@shared_task
def today_request(request):
    request = request + 1
    if request >= 500:
        return False
    return True


@shared_task
@app.task(rate_limit='1/m', time_limit="5")
def crwaling_enter_info(company_name, url):
    # i = app.control.inspect()
    # print(i.scheduled())
    # print(i.active())
    # print(i.reserved())
    company_name = company_name.replace(' ', '').replace('\n', '').lstrip('(주)').rstrip('(주)')
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
        if time_cal <= now :
            print("7일 이상 지났습니다.")
            saramin = SaraminInfo.objects.get(enter=object)
            jobkorea = JobKoreaInfo.objects.get(enter=object)
            jobplanet = JobPlanetInfo.objects.get(enter=object)
            kreditjob = KreditJobInfo.objects.get(enter=object)
            company_name = saramin.enter.enter_name

            saramin = GetSaraminEnterInfo(company_csn=saramin.company_code, company_name=company_name, company_url=saramin.url)
            enter, saramin_location = saramin.get_company_info(url)

            jobkorea = GetJobKoreaInfo(enter=enter, company_url=jobkorea.url)
            jobkorea_location = jobkorea.get_company_info(company_name=company_name)

            jobplanet = GetJobPlanetInfo(enter=enter, company_url=jobplanet.url)
            jobplanet_location = jobplanet.get_company_info(company_name=company_name)

            kreditjob = GetKreditJobInfo(enter=enter, company_url=kreditjob.url)
            kreditjob.get_company_info(company_name=company_name, saramin_location=saramin_location,
                                       jobkorea_location=jobkorea_location, jobplanet_location=jobplanet_location)
        else:
            print("7일이 지나지 않았습니다. 7일이 지난 후에 신청하세요")
            raise Exception
    else:
        saramin = GetSaraminEnterInfo()
        enter, saramin_location = saramin.get_company_info(saramin_url=url, company_name=company_name)

        jobkorea = GetJobKoreaInfo(enter=enter)
        jobkorea_location = jobkorea.get_company_info(company_name=company_name)
        jobplanet = GetJobPlanetInfo(enter=enter)
        jobplanet_location = jobplanet.get_company_info(company_name=company_name)
        kreditjob = GetKreditJobInfo(enter=enter)
        kreditjob.get_company_info(company_name=company_name, saramin_location=saramin_location, jobkorea_location=jobkorea_location, jobplanet_location=jobplanet_location)


@shared_task
def search_job_task(context, page, search_job):
    return SearchJob(context, page, search_job)