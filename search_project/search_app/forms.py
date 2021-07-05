from django.core.exceptions import ValidationError

from .models import MyEnterprise
from bootstrap_modal_forms.forms import BSModalModelForm
from django.forms import forms
from django.shortcuts import get_object_or_404


class MyEnterpriseForm(BSModalModelForm):
    class Meta:
        model = MyEnterprise
        exclude = ['author',]

    def clean_company(self, *args, **kwargs):
        company = self.cleaned_data.get('company')
        try:
            # object = get_object_or_404(MyEnterprise, author=self.request.user.pk, company=company)
            MyEnterprise.objects.filter(author=self.request.user.pk, company=company)
            raise forms.ValidationError(company + '가 이미 존재합니다')
        except Exception as e:
            print(e)
            return company

