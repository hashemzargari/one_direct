from django.contrib.auth import get_user_model
from url_shortener.models import Url, VisitUrl
from celery import shared_task


@shared_task
def add_url_to_db(long_version, short_version, re_path, user):
    user = get_user_model().objects.filter(pk=user).first()
    Url.objects.create(long_version=long_version, short_version=short_version, re_path=re_path, user=user)


@shared_task
def add_visit_url(url, client_browser, client_device, client_ip):
    url = Url.objects.filter(url=url).first()
    VisitUrl.objects.create(url=url, client_browser=client_browser,
                            client_device=client_device, client_ip=client_ip)
