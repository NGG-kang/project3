# search_app/urls.py

from django.urls import path
from search_app import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'post', views.PostView)
router.register(r'comment', views.CommentView)

app_name = 'search_app'
urlpatterns = [
    path('api/', views.SearchView.as_view()),

    # path('search_job/', views.search_jop_view, name="search_job"),
    path('search_job/', views.SearchJobTemplateView.as_view(), name="search_job"),
    path('search_company/',views.SearchCompanyListView.as_view(), name="search_company"),
    path('task_list/', views.TaskTemplateView.as_view(), name="task_list"),

    path('create_enter/', views.EnterCreateView.as_view(), name="create_enter"),
    path('update_enter/<int:pk>/', views.EnterUpdateView.as_view(), name='update_enter'),
    path('read_enter/<int:pk>/', views.EnterReadView.as_view(), name='read_enter'),
    path('delete_enter/<int:pk>/', views.EnterDeleteView.as_view(), name='delete_enter'),

    path('apply_enter_info/', views.apply_enter_info, name='apply_enter_info'),


    path('crwaling_info/', views.CrawlingInfoList.as_view(), name='crwaling_info'),
    path('crwaling_info_saramin/<int:pk>/', views.SaraminModalView.as_view(), name='crwaling_info_saramin'),
    path('crwaling_info_jobkorea/<int:pk>/', views.JobkoreaModalView.as_view(), name='crwaling_info_jobkorea'),
    path('crwaling_info_jobplanet/<int:pk>/', views.JobplanetModalView.as_view(), name='crwaling_info_jobplanet'),
    path('crwaling_info_kreditjob/<int:pk>/', views.KreditJobModalView.as_view(), name='crwaling_info_kreditjob'),

    path('search_job/users_enters_info/', views.GetUsersEntersInfo.as_view(), name='users_enters_info'),
    path('search_job/<int:pk>/user_enter_info/', views.GetUserEnterInfo.as_view(), name='user_enter_info'),
]

urlpatterns += router.urls