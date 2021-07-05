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
    path('search_job/', views.SearchJobTemplateView.as_view(), name="search_job"),
    path('search_company/', views.SearchCompanyTemplateView.as_view(), name="search_company"),
    path('create_enter/', views.EnterCreateView.as_view(), name="create_enter"),
    path('update_enter/<int:pk>/', views.EnterUpdateView.as_view(), name='update_enter'),
    path('read_enter/<int:pk>/', views.EnterReadView.as_view(), name='read_enter'),
    path('delete_enter/<int:pk>/', views.EnterDeleteView.as_view(), name='delete_enter'),

    path('search_job/users_enters_info/', views.GetUsersEntersInfo.as_view(), name='users_enters_info'),
    path('search_job/<int:pk>/user_enter_info/', views.GetUserEnterInfo.as_view(), name='user_enter_info'),
]

urlpatterns += router.urls