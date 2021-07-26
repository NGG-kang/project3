# views.py
import ast
import json
from django.conf import settings
from django.http.response import JsonResponse
import requests
import operator

from django.db.models.expressions import Subquery
from search_app.search import SearchJob

import httpx
import logging
from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.template import loader
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy, reverse

from django.views.generic import TemplateView
from bootstrap_modal_forms.generic import (
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)
from .forms import MyEnterpriseForm
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import HTTP_HEADER_ENCODING, status

from .models import Post, Comment, MyEnterprise, MyEnterPhoto, CrwalingModel, SaraminInfo, JobKoreaInfo, JobPlanetInfo, KreditJobInfo, CrwalingPhotos
from .Serailizer import PostSerializer, CommentSerializer

from elasticsearch import Elasticsearch
from search_app.tasks import crwaling_enter_info
from celery.result import ResultBase
from search_project.celery import app
from django.core.cache import cache
logger = logging.getLogger(__name__)

class SearchView(APIView):

    def get(self, request):
        es = Elasticsearch(hosts='localhost', port=9200)

        # 검색어
        search_word = request.query_params.get('search')

        if not search_word:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'search word param is missing'})
        docs = es.search(index='dictionary',
                         body={
                             "query": {
                                 "multi_match": {
                                     "query": search_word,
                                     "fields": ["title", "keyword", "field", "type"]
                                 }
                             }
                         })

        data_list = docs['hits']

        return Response(data_list)


class PostView(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class CommentView(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        pass

# search_job page 이동시에 쓰임
class SearchJobTemplateView(TemplateView):
    template_name="search_job.html"

    def get(self, request, *args, **kwargs):
        search_job = request.GET.get("search_job")
        context = self.get_context_data(**kwargs)
        if search_job:
            page = request.GET.get('page')
            if not page:
                page = "1"
            context = SearchJob(context, page, search_job)
        return render(template_name="search_job.html", context=context, request=request)

# search_job 검색시 ajax용도 그냥 함수로 구현해도 되는데 ㅎㅎ;;
class SearchBodyTemplateView(TemplateView):
    template_name = "search_job.html"

    def get(self, request, *args, **kwargs):
        search_job = request.GET.get("search_job")
        context = self.get_context_data(**kwargs)
        if search_job:
            page = request.GET.get('page')
            if not page:
                page = "1"
            context = SearchJob(context, page, search_job)
        return render(template_name="search_body.html", context=context, request=request)


# 크롤링된 기업들 검색
class SearchCompanyListView(LoginRequiredMixin, generic.ListView):
    template_name = 'crawling_info_list.html'
    model = CrwalingModel
    queryset = CrwalingModel.objects.all()
    context_object_name = "crawling"
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        company_name = self.request.GET.get('search_company')
        logger.info(company_name)
        self.object_list = self.get_queryset().filter(enter_name__contains=company_name)
        context = self.get_context_data()
        return self.render_to_response(context)


class SearchCompanyBodyListView(LoginRequiredMixin, generic.ListView):
    template_name = 'crawling_info_list_body.html'
    model = CrwalingModel
    queryset = CrwalingModel.objects.all()
    context_object_name = "crawling"
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        company_name = self.request.GET.get('search_company')
        logger.info(company_name)
        self.object_list = self.get_queryset().filter(enter_name__contains=company_name)
        context = self.get_context_data()
        return self.render_to_response(context)

# Task들 목록 보여주기
class TaskTemplateView(TemplateView):

    def get(self, request, *args, **kwargs):
        tasks_url = 'http://localhost:5555/api/tasks'
        # if settings.debug == "True":
        #     tasks_url = 'http://127.0.0.1:5555/api/tasks'
        # else:
        #     tasks_url = 'http://host.docker.internal:5555/api/tasks'
        logger.info(tasks_url)
        res = requests.get(tasks_url).text
        task = json.loads(res)
        return render(template_name="task_view.html", context={'task': sorted(task.items())}, request=request)


class Index(generic.ListView):
    model = MyEnterprise
    context_object_name = 'enters'
    template_name = 'enter_list.html'


class EnterCreateView(BSModalCreateView):
    template_name = 'enter_form/create_enter.html'
    form_class = MyEnterpriseForm
    success_message = '메모 생성 성공'

    def form_valid(self, form):
        logger.info("하는거 맞니?")
        logger.info("생성 확인중")
        form.instance.author = self.request.user
        return super(EnterCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('search_app:user_enter_info', kwargs={'pk': self.request.user.pk})


# Update
class EnterUpdateView(BSModalUpdateView):
    model = MyEnterprise
    template_name = 'enter_form/update_enter.html'
    form_class = MyEnterpriseForm
    success_message = 'Success: enter was updated.'

    def get_success_url(self):
        return reverse_lazy('search_app:user_enter_info', kwargs={'pk': self.kwargs['pk']})


# Read
class EnterReadView(BSModalReadView):
    model = MyEnterprise
    template_name = 'enter_form/read_enter.html'


# Delete
class EnterDeleteView(BSModalDeleteView):
    model = MyEnterprise
    template_name = 'enter_form/delete_enter.html'
    success_message = 'Success: Enter was deleted.'

    def get_success_url(self):
        return reverse_lazy('search_app:user_enter_info', kwargs={'pk': self.request.user.pk})


# 공유한 유저들 enter 리스트
class GetUsersEntersInfo(generic.ListView):
    template_name = 'enter_info/users_enters_info.html'
    model = MyEnterprise
    queryset = MyEnterprise.objects.all().select_related('author')
    ordering = ['-id']
    context_object_name = "users_enters_list"


# 로그인 유저 enter 리스트뷰
class GetUserEnterInfo(LoginRequiredMixin, generic.ListView):
    template_name = 'enter_info/user_enter_info.html'
    context_object_name = "user_enter_info"

    def get_queryset(self):
        queryset = MyEnterprise.objects.filter(
            author=self.kwargs['pk']).select_related('author')

        if not queryset:
            queryset = ""
        return queryset


# 로그인 유저 enter 디테일뷰
class GetUserEnterInfoDetail(LoginRequiredMixin, generic.DetailView):
    template_name = 'enter_info/user_enter_info_detail.html'

    def get_queryset(self):
        queryset = MyEnterprise.objects.filter(
            author=self.kwargs['pk'], title=self.kwargs['company'])

        if not queryset:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return queryset


# 크롤링 신청 함수
# TODO: celery 넘어가기 전에 하루 request 500번 미만 체크
# TODO: 여러 요청해도 한개의 크롤링만 돌아가도록
def apply_enter_info(request):
    logger.info("크롤링 리퀘스트 들어옴")
    if request.method == "POST":
        try:
            company_name, company_link = request.POST.get(
                "company_name"), request.POST.get("company_link")
            logger.info("시작")
            logger.info(company_name, company_link)
            try:
                cache_val = cache.get('today_request', 0)
                if not cache_val:
                    cache.set('today_request', 0)
                # 일단 오늘 리퀘스트 올려놓고
                cache.incr('today_request')
                logger.info(cache.get('today_request'))

                # 만약 500건이 넘었다면 취소
                if cache.get('today_request') >= 500:
                    cache.decr('today_request')
                    messages.warning(request, '하루 최대 크롤링 요청에 도달했습니다. 내일 다시 신청이 가능합니다. (하루 최대 500건)')
                    return HttpResponse(status=400)
                # 아니라면 줄여놓고 크롤링 끝내고 다시 올려놓기
                else:
                    logger.info('500건 미만, 크롤링 시작합니다.')
                    cache.decr('today_request')
                    logger.info(cache.get('today_request'))
            except Exception as e:
                logger.warning(e)
                logger.warning("캐시부분 에러")
                messages.warning(request, '캐시부분 서버에 에러가 있습니다. 제작자에게 문의 해주세요')
                return HttpResponse(status=500)
            try:
                # delay에 queue를 넣는 방법이 있나?
                # crwaling_enter_info.delay(company_name=company_name, url=company_link)
                crwaling_enter_info.apply_async(kwargs={"company_name": company_name, "url": company_link}, countdown=1, queue='crwaling_enter_info')
            except Exception as e:
                logger.warnin(e)
                logger.warning("크롤링 부분 에러")
                return HttpResponse(status=500)
            
            # 메세지는 스택처럼 쌓여서 나중에 한번에 보일수 있음.
            messages.success(request, '크롤링 신청 완료.')
            return HttpResponse(status=204)

        except Exception as e:
            logger.info(e)
            logger.info("중간에 에러 발생")
            return HttpResponse(status=500)


def is_company(request):
    if request.method == "GET":
        company_name = request.GET.get('company_name')
        logger.info(company_name)
        object = CrwalingModel.objects.get(company_name=company_name)
        if object:
            return HttpResponse(status=200)
    return HttpResponse(status=400)



# 크롤링된 기업들 전부 보여주는 페이지
class CrawlingInfoList(LoginRequiredMixin, generic.ListView):
    template_name = 'crawling_info_list.html'
    model = CrwalingModel
    context_object_name = "crawling"
    paginate_by = 50

    def get_queryset(self):
        queryset = CrwalingModel.objects.order_by('enter_name','-created_at').distinct('enter_name')
        queryset = sorted(queryset, key=operator.attrgetter('created_at'), reverse=True)
        return queryset






class SaraminModalView(BSModalReadView):
    model = CrwalingModel
    template_name = 'crawl_enter/saramin.html'
    context_object_name = "crawling_info"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        saramin = SaraminInfo.objects.get(enter=self.object)
        photos = CrwalingPhotos.objects.filter(
            saramin_info=saramin).order_by('created_at')
        context = self.get_context_data(object=self.object)
        context["info"] = saramin
        context['photos'] = photos
        return self.render_to_response(context)


class JobkoreaModalView(BSModalReadView):
    model = CrwalingModel
    template_name = 'crawl_enter/jobkorea.html'
    context_object_name = "crawling_info"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        jobkorea = JobKoreaInfo.objects.get(enter=self.object)
        photos = CrwalingPhotos.objects.filter(jobkorea_info=jobkorea)
        context = self.get_context_data(object=self.object)
        context["info"] = jobkorea
        context['photos'] = photos
        return self.render_to_response(context)


class JobplanetModalView(BSModalReadView):
    model = CrwalingModel
    template_name = 'crawl_enter/jobplanet.html'
    context_object_name = "crawling_info"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        jobplanet = JobPlanetInfo.objects.get(enter=self.object)
        photos = CrwalingPhotos.objects.filter(jobplanet_info=jobplanet)
        context = self.get_context_data(object=self.object)
        context["info"] = jobplanet
        context['photos'] = photos
        return self.render_to_response(context)


class KreditJobModalView(BSModalReadView):
    model = CrwalingModel
    template_name = 'crawl_enter/kreditjob.html'
    context_object_name = "crawling_info"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        kreditjob = KreditJobInfo.objects.get(enter=self.object)
        photos = CrwalingPhotos.objects.filter(kreditjob_info=kreditjob)
        context = self.get_context_data(object=self.object)
        context["info"] = kreditjob
        context['photos'] = photos
        return self.render_to_response(context)
