# views.py
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import Http404, HttpResponse
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
from rest_framework import status

from .models import Post, Comment, MyEnterprise, MyEnterPhoto, CrwalingModel, SaraminInfo, JobKoreaInfo, JobPlanetInfo, KreditJobInfo, CrwalingPhotos
from .Serailizer import PostSerializer, CommentSerializer

from elasticsearch import Elasticsearch
from search_app.tasks import search_job_task, crwaling_enter_info


class SearchView(APIView):

    def get(self, request):
        es = Elasticsearch(hosts='localhost',port=9200)

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


class SearchJobTemplateView(TemplateView):
    template_name = "search_job.html"

    def get(self, request, *args, **kwargs):
        search_job = request.GET.get("search_job")
        search_company = request.GET.get("search_company")
        # get_company = request.GET.get("company")
        context = self.get_context_data(**kwargs)

        if search_job:
            page = request.GET.get('page')
            if not page:
                page = "1"
            context = search_job_task(context, page, search_job)
        return render(template_name="search_job.html", context=context, request=request)


class SearchCompanyTemplateView(TemplateView):
    template_name = "search_company.html"

    def get(self, request, *args, **kwargs):
        search_company = request.GET.get("search_company")
        context = self.get_context_data(**kwargs)

        if search_company:
            context = search_job_task(context, search_company)
        return render(template_name="search_company.html", context=context, request=request)


class Index(generic.ListView):
    model = MyEnterprise
    context_object_name = 'enters'
    template_name = 'enter_list.html'


class EnterCreateView(BSModalCreateView):
    template_name = 'enter_form/create_enter.html'
    form_class = MyEnterpriseForm
    success_message = '메모 생성 성공'

    def form_valid(self, form):
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
        queryset = MyEnterprise.objects.filter(author=self.kwargs['pk']).select_related('author')

        if not queryset:
            queryset = ""
        return queryset


# 로그인 유저 enter 디테일뷰
class GetUserEnterInfoDetail(LoginRequiredMixin, generic.DetailView):
    template_name = 'enter_info/user_enter_info_detail.html'

    def get_queryset(self):
        queryset = MyEnterprise.objects.filter(author=self.kwargs['pk'], title=self.kwargs['company'])

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
# TODO: celery 넘어가기 전에 request 500번 미만, 이미 있으면 7일 이내인지 확인하기
def apply_enter_info(request):
    if request.method == "POST":
        try:
            company_name = request.POST.get("company_name")
            company_link = request.POST.get("company_link")
            crwaling_enter_info(company_name, company_link)
            return HttpResponse(status=201)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)


# 크롤링 된거 보여주는 함수
def Is_crawler_info(request):
    if request.method == "POST":
        try:
            company_name = request.POST.get("company_name")
            company_link = request.POST.get("company_link")
            crwaling_enter_info(company_name, company_link)
            return HttpResponse(status=201)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

# 크롤링된 기업들 전부 보여주는 페이지
class CrawlingInfoList(LoginRequiredMixin, generic.ListView):
    template_name = 'crawling_info_list.html'
    model = CrwalingModel
    queryset = CrwalingModel.objects.order_by('enter_name', '-created_at').distinct('enter_name')
    # queryset = CrwalingModel.objects.all().distinct()
    context_object_name = "crawling"


class SaraminModalView(BSModalReadView):
    model = CrwalingModel
    template_name = 'crawl_enter/saramin.html'
    context_object_name = "crawling_info"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        saramin = SaraminInfo.objects.get(enter=self.object)
        photos = CrwalingPhotos.objects.filter(saramin_info=saramin)
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
