from django.shortcuts import render
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalLoginView, BSModalCreateView
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from search_app.models import MyEnterprise


class CustomLoginView(BSModalLoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'login.html'
    success_message = 'Success: You were successfully logged in.'
    extra_context = dict(success_url=reverse_lazy('search_app:search_job'))
    success_url = reverse_lazy('search_app:search_job')


class SignUpView(BSModalCreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_message = 'Success: Sign up succeeded. You can now Log in.'
    success_url = reverse_lazy('search_app:search_job')


class ProfileView(LoginRequiredMixin,generic.ListView):
    template_name = "profile.html"
    model = MyEnterprise

    def get(self, request, *args, **kwargs):
        user = request.user
        objects = MyEnterprise.objects.filter(author=user)
        return render(request, template_name="profile.html", context=objects)