from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializer import UrlSerializer
from .permissions import IsOwnerOrForbidden
from url_shortener.models import Url
from url_shortener.utils.url_shortner import make_shorten, check_uniq
from url_shortener.utils.validators import url_validator
from url_shortener.api import tasks


class UrlListApiView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser | IsOwnerOrForbidden]
    serializer_class = UrlSerializer

    def get_queryset(self):
        return Url.objects.filter(user=self.request.user)


class UrlRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser | IsOwnerOrForbidden]
    serializer_class = UrlSerializer

    def get_queryset(self):
        return Url.objects.filter(user=self.request.user)


class UrlCreateApiView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UrlSerializer

    def post(self, request, *args, **kwargs):
        # data
        _data = request.data
        _re_path = _data.get('re_path', None)
        _long_version = url_validator(_data.get('long_version', None))
        if not _long_version:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # generate short url
        if _re_path:
            short_version = make_shorten(re_path=_re_path)
        else:
            short_version = make_shorten()
        try_slug = 0
        while not check_uniq(short_version):
            short_version = make_shorten(try_slug=try_slug + 1)
        # add url to redis
        cache.set(_long_version, short_version, None)
        cache.set(short_version, _long_version, None)
        # task to save url in db
        tasks.add_url_to_db.delay(long_version=_long_version, short_version=short_version, re_path=_re_path,
                                  user=request.user.id)
        # return the short_version url
        return Response(data={'short_version': short_version}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def redirect_client(request, short_version):
    # read long_url from redis and check exist
    _long_version = cache.get(short_version)

    # if cache missed
    if _long_version is None:
        # we want handle response, rather than get_object_or_404
        _url_ = Url.objects.filter(short_version=short_version)
        if _url_.count() > 0:
            _long_version = _url_.first().long_version

    if _long_version is not None:
        # get client info

        # device

        user_device = 'undefined'
        if request.user_agent.is_pc:
            user_device = 'pc'
        elif request.user_agent.is_mobile:
            user_device = 'mobile'
        elif request.user_agent.is_tablet:
            user_device = 'tablet'

        # browser

        user_browser = 'undefined'
        if request.user_agent.browser:
            user_browser = str(request.user_agent.browser.family) + ' ' + str(request.user_agent.browser.version)

        # user ip

        user_ip = request.META['REMOTE_ADDR']

        # add client info to redis for analytics

        _cache_name = str(short_version) + '_visited'
        _old_clients = cache.get(_cache_name)
        if not _old_clients:
            _old_clients = []
        _old_clients += [
            {str(timezone.now()):
                 {'user_ip': user_ip,
                  'user_browser': user_browser,
                  'user_device': user_device}}]
        cache.set(_cache_name, _old_clients, None)

        # increment count in redis

        _cache_name_count = str(short_version) + '_visited_count'
        _old_clients_count = cache.get(_cache_name_count)
        if not _old_clients_count:
            _old_clients_count = 0
        _old_clients_count = int(_old_clients_count)
        cache.set(_cache_name_count, _old_clients_count + 1, None)

        # task to add client info to db and automated increment with save method in model

        tasks.add_visit_url.delay(short_version=str(short_version), client_browser=str(user_browser),
                                  client_device=str(user_device), client_ip=str(user_ip))

        # redirect user
        return HttpResponseRedirect(_long_version)

    return Response(status=status.HTTP_404_NOT_FOUND)
