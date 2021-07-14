from django.contrib import admin
from search_app import models
# Register your models here.


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MyEnterprise)
class MyEnterpriseAdmin(admin.ModelAdmin):
    pass

@admin.register(models.MyEnterPhoto)
class EnterPhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CrwalingModel)
class CrwalingModelAdmin(admin.ModelAdmin):
    list_display = ['enter_name', 'created_at', 'updated_at']
    pass

@admin.register(models.SaraminInfo)
class SaraminInfoAdmin(admin.ModelAdmin):
    list_display = ['enter', 'created_at', 'updated_at']

    def created_at(self, obj):
        return obj.enter.created_at

    def updated_at(self, obj):
        return obj.enter.updated_at
    pass

@admin.register(models.JobKoreaInfo)
class JobKoreaInfoAdmin(admin.ModelAdmin):
    list_display = ['enter', 'created_at', 'updated_at']

    def created_at(self, obj):
        return obj.enter.created_at

    def updated_at(self, obj):
        return obj.enter.updated_at
    pass

@admin.register(models.JobPlanetInfo)
class JobPlanetInfoAdmin(admin.ModelAdmin):
    list_display = ['enter', 'created_at', 'updated_at']

    def created_at(self, obj):
        return obj.enter.created_at

    def updated_at(self, obj):
        return obj.enter.updated_at
    pass

@admin.register(models.KreditJobInfo)
class KreditJobInfo(admin.ModelAdmin):
    list_display = ['enter', 'created_at', 'updated_at']

    def created_at(self, obj):
        return obj.enter.created_at

    def updated_at(self, obj):
        return obj.enter.updated_at
    pass

@admin.register(models.CrwalingPhotos)
class CrwalingPhotosAdmin(admin.ModelAdmin):
    list_display = ['photo_name', 'created_at']

    def photo_name(self, object):
        return object.photo.name.split('/')[-1]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter().select_related('saramin_info', 'jobkorea_info', 'jobplanet_info', 'kreditjob_info',
                                              'saramin_info__enter')
        return qs.filter(author=request.user)
    pass