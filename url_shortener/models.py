from django.db import models
from django.contrib.auth import get_user_model


class BaseInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Url(BaseInfo):
    long_version = models.URLField()
    short_version = models.CharField(max_length=155, unique=True)
    re_path = models.CharField(max_length=100, blank=True, default=None)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='urls')
    redirect_count = models.PositiveBigIntegerField(blank=True, default=0)

    def __str__(self):
        return f'id: {self.id},' \
               f' long_version: {self.long_version},' \
               f' short_version: {self.short_version}'


class VisitUrl(BaseInfo):
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name='visited')
    client_browser = models.CharField(max_length=255)
    client_device = models.CharField(max_length=255)
    client_ip = models.CharField(max_length=15)

    def __str__(self):
        return f'id: {self.id},' \
               f' browser: {self.client_browser},' \
               f' device: {self.client_device},' \
               f' ip: {self.client_ip}'

    def save(self, *args, **kwargs):
        # first everything saved in cache and then save to database !
        _url = Url.objects.filter(long_version=self.url).first()
        if _url:
            visit_count = VisitUrl.objects.filter(url=self.url).count()
            _url.redirect_count = visit_count + 1
            _url.save()
        super().save(*args, **kwargs)
