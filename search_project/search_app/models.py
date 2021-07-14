import io
import os

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

class TimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# 게시판용으로 만들었는데 안 쓰는중
class Post(TimeModel):
    author = models.ForeignKey(on_delete=models.CASCADE, to=get_user_model())
    title = models.CharField(max_length=20)
    content = models.TextField(max_length=300)
    photo = models.ImageField(upload_to="search_app/%Y/%m/%d", blank=True)

    def __str__(self):
        return self.title


class Comment(TimeModel):
    author = models.ForeignKey(on_delete=models.CASCADE, to=get_user_model())
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=90)

    def __str__(self):
        return self.post.title


# 게시판용 MyEnterprise, MyEnterPhoto
class MyEnterprise(TimeModel):
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    name = models.CharField(blank=True, max_length=100)
    link = models.SlugField(blank=True, max_length=1000)
    memo = models.TextField(blank=True, max_length=1000)
    location = models.CharField(blank=True, max_length=100)
    photo = models.ForeignKey("MyEnterPhoto", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.company

    def get_absolute_url(self):
        return reverse('search_app:post_detail', args=[self.request.user.pk])



# 여기부터 게시글 모델들
class MyEnterPhoto(TimeModel):
    my_enter = models.ForeignKey(MyEnterprise, models.CASCADE)
    photo = models.ImageField(blank=True, upload_to="search_job/%Y/%m/%d")

    def __str__(self):
        return self.photo.name


class Select(models.TextChoices):
    SARAMIN = 0
    PUBLIC = 1
    PRIVATE = 2
    PARTIAL = 3


class EnterInfo(TimeModel):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class EnterInfoPhotos(models.Model):
    enter = models.ForeignKey(EnterInfo, models.CASCADE)
    photo = models.ImageField(blank=True)

    def __str__(self):
        return self.enter.name


class EnterUrl(models.Model):
    enter = models.ForeignKey(EnterInfo, models.CASCADE)
    url = models.SlugField(max_length=1000)


# 기업정보 요청으로 자동으로 생성되는 모델 데이터들
# 사람인 기업정보 이름을 기준으로 한다
# 동명기업 처리는 name, location 전부 같은지 비교
# 여기부터 크롤링 모델들
class CrwalingModel(TimeModel):
    enter_name = models.CharField(max_length=50)

    def __str__(self):
        return self.enter_name

    class Meta:
        ordering = ['-created_at', 'enter_name']


class CrwalingBaseModel(models.Model):
    enter = models.OneToOneField(CrwalingModel, on_delete=models.CASCADE)
    company_code = models.CharField(max_length=1000, blank=True)
    location = models.CharField(max_length=1000, blank=True)
    url = models.SlugField(max_length=1000, blank=True)
    upload_to_path = models.CharField(max_length=2000, blank=True)


    def __str__(self):
        return self.enter.enter_name

    class Meta:
        abstract = True


@receiver(post_save, sender=CrwalingModel)
def create_Post(sender, instance, created, **kwargs):
    if created:
        if instance not in ['SaraminInfo', 'JobKoreaInfo', 'JobPlanetInfo', 'KreditJobInfo']:
            SaraminInfo.objects.create(enter=instance)
            JobKoreaInfo.objects.create(enter=instance)
            JobPlanetInfo.objects.create(enter=instance)
            KreditJobInfo.objects.create(enter=instance)


class SaraminInfo(CrwalingBaseModel):
    # name = models.CharField(max_length=7, default='saramin')
    pass


class JobKoreaInfo(CrwalingBaseModel):
    # name = models.CharField(max_length=8, default='jobkorea')
    pass


class JobPlanetInfo(CrwalingBaseModel):
    # name = models.CharField(max_length=9, default='jobplanet')
    pass


class KreditJobInfo(CrwalingBaseModel):
    # name = models.CharField(max_length=9, default='kreditjob')
    jobdom_list = ArrayField(models.CharField(max_length=1000, blank=True), default=list, )
    pass

# 경로: 회사이름 -> 크롤링회사 -> 코드 -> 날짜
# 이미지이름: 회사이름_회사코드_기타내용.png
def crwaling_photo_path(instance, filename):
    if instance.jobkorea_info:
        return '{0}/{1}'.format(instance.jobkorea_info.upload_to_path, filename)
    elif instance.saramin_info:
        return '{0}/{1}'.format(instance.saramin_info.upload_to_path, filename)
    elif instance.jobplanet_info:
        return '{0}/{1}'.format(instance.jobplanet_info.upload_to_path, filename)
    elif instance.kreditjob_info:
        return '{0}/{1}'.format(instance.kreditjob_info.upload_to_path, filename)

class CrwalingPhotos(TimeModel):
    photo = models.ImageField(upload_to=crwaling_photo_path, max_length=1000)
    saramin_info = models.ForeignKey(SaraminInfo, on_delete=models.CASCADE, blank=True, null=True)
    jobkorea_info = models.ForeignKey(JobKoreaInfo, on_delete=models.CASCADE, blank=True, null=True)
    jobplanet_info = models.ForeignKey(JobPlanetInfo, on_delete=models.CASCADE, blank=True, null=True)
    kreditjob_info = models.ForeignKey(KreditJobInfo, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.saramin_info:
            return "saramin_"+self.saramin_info.enter.enter_name+"_"+(self.photo.name.split("/")[-1])
        elif self.jobkorea_info:
            return "jobkorea_"+self.jobkorea_info.enter.enter_name+"_"+(self.photo.name.split("/")[-1])
        elif self.jobplanet_info:
            return "jobplanet_"+self.jobplanet_info.enter.enter_name+"_"+(self.photo.name.split("/")[-1])
        elif self.kreditjob_info:
            return "kreditjob_"+self.kreditjob_info.enter.enter_name+"_"+(self.photo.name.split("/")[-1])

    class Meta:
        ordering = ['-created_at', 'saramin_info', 'jobkorea_info', 'jobplanet_info', 'kreditjob_info']




