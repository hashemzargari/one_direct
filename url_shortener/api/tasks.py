from url_shortener.models import Url
from celery import shared_task


@shared_task
def add_url_to_db(long_version, short_version, re_path, user):
    Url.objects.create(long_version=long_version, short_version=short_version, re_path=re_path, user=user)
