from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class TimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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


class MyEnterprise(TimeModel):
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    name = models.CharField(blank=True, max_length=100)
    link = models.SlugField(blank=True, max_length=1000)
    memo = models.TextField(blank=True, max_length=1000)
    location = models.CharField(blank=True, max_length=100)
    photo = models.ForeignKey("EnterPhoto", on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.company

    def get_absolute_url(self):
        return reverse('search_app:post_detail', args=[self.request.user.pk])


class EnterPhoto(TimeModel):
    enter = models.ForeignKey(MyEnterprise, models.CASCADE)
    photo = models.ImageField(blank=True, upload_to="search_job/%Y/%m/%d")

    def __str__(self):
        return self.photo.name

