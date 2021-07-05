# views.py
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import Http404
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
from asgiref.sync import sync_to_async
from .forms import MyEnterpriseForm

import requests
import time
from bs4 import BeautifulSoup

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .models import Post, Comment, MyEnterprise, EnterPhoto
from .Serailizer import PostSerializer, CommentSerializer

from elasticsearch import Elasticsearch
from django.shortcuts import get_object_or_404
from search_app.search import SearchJob, SearchCompany



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
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        search_job = request.GET.get("search_job")
        search_company = request.GET.get("search_company")
        # get_company = request.GET.get("company")
        context = self.get_context_data(**kwargs)

        if search_job:
            page = request.GET.get('page')
            if not page:
                page = "1"
            context = SearchJob(context, page, search_job)
        return render(template_name="search.html", context=context, request=request)


class SearchCompanyTemplateView(TemplateView):
    template_name = "search_company.html"

    def get(self, request, *args, **kwargs):
        search_company = request.GET.get("search_company")
        context = self.get_context_data(**kwargs)

        if search_company:
            context = SearchCompany(context, search_company)
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
