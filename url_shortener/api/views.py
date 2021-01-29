from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.core.cache import cache
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializer import UrlSerializer, VisitUrlSerializer
from .permissions import IsOwnerOrForbidden
from url_shortener.models import Url, VisitUrl
from url_shortener.utils.url_shortner import make_shorten, check_uniq
from url_shortener.utils.validators import url_validator
from url_shortener.api.tasks import add_url_to_db


# class UrlViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAdminUser | IsOwnerOrForbidden]
#     serializer_class = UrlSerializer
#
#     def get_queryset(self):
#         return Url.objects.filter(user=self.request.user)
#
#     # def list(self, request, *args, **kwargs):
#     #     queryset = self.filter_queryset(self.get_queryset())
#     #
#     #     page = self.paginate_queryset(queryset)
#     #     if page is not None:
#     #         serializer = self.get_serializer(page, many=True)
#     #         return self.get_paginated_response(serializer.data)
#     #
#     #     serializer = self.get_serializer(queryset, many=True)
#     #     return Response(serializer.data)

class UrlListApiView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser | IsOwnerOrForbidden]

    def get_queryset(self):
        return Url.objects.filter(user=self.request.user)


class UrlRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser | IsOwnerOrForbidden]

    def get_queryset(self):
        return Url.objects.filter(user=self.request.user)


class UrlCreateApiView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UrlSerializer

    def post(self, request, *args, **kwargs):
        # data
        _data = self.request.data
        _re_path = _data.get('path', None)
        _long_version = url_validator(_data.get('url', None))
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
        cache.set(_long_version, short_version)
        cache.set(short_version, _long_version)
        # task to save url in db
        add_url_to_db.delay(long_version=_long_version, short_version=short_version, re_path=_re_path,
                            user=self.request.user)
        # return the short_version url
        return Response(data={'short_version': short_version}, status=status.HTTP_201_CREATED)


@api_view()  # only get method
def redirect_client(request):
    # get client info
    # task to add client info to redis for analytics
    # task to increment count first in redis
    # task to add client info to db and automated increment with save method in model
    # read long_url from redis
    # redirect user
    pass
