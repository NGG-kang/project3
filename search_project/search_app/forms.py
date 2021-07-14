from django.core.exceptions import ValidationError

from .models import MyEnterprise, SaraminInfo, JobKoreaInfo, JobPlanetInfo, KreditJobInfo, CrwalingPhotos
from bootstrap_modal_forms.forms import BSModalModelForm
from django.forms import forms
from django.shortcuts import get_object_or_404


class MyEnterpriseForm(BSModalModelForm):
    class Meta:
        model = MyEnterprise
        exclude = ['author', ]

    def clean_company(self, *args, **kwargs):
        company = self.cleaned_data.get('company')
        try:
            # object = get_object_or_404(MyEnterprise, author=self.request.user.pk, company=company)
            object = MyEnterprise.objects.filter(author=self.request.user.pk, company=company)
            if object:
                raise forms.ValidationError(company + '가 이미 존재합니다')
            return company
        except Exception as e:
            print(e)
            return company


class SaraminForm(BSModalModelForm):
    class Meta:
        model = SaraminInfo
        fields = ('__all__')


class JobKoreaForm(BSModalModelForm):
    class Meta:
        model = JobKoreaInfo
        fields = ('__all__')


class JobPlanetForm(BSModalModelForm):
    class Meta:
        model = JobPlanetInfo
        fields = ('__all__')


class KreditJobForm(BSModalModelForm):
    class Meta:
        model = KreditJobInfo
        fields = ('__all__')


class CrwalingPhotos(BSModalModelForm):
    class Meta:
        model = CrwalingPhotos
        fields = ('__all__')
