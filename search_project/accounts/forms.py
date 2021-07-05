from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from django.contrib.auth.forms import UserCreationForm


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class CustomUserCreationForm(PopRequestMixin, CreateUpdateAjaxMixin,
                             UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password1', 'password2']