from django.urls import path
from django.contrib.auth.views import LogoutView
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(),  name='logout')
]