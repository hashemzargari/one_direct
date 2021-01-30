from rest_framework.response import Response
from rest_framework import status, permissions
from url_shortener.models import Url
from rest_framework.decorators import api_view
from django.core.cache import cache


@api_view(['GET'])
def visited_link_analytics(request, url):
    long_version = cache.get(url)
    if long_version:
        _url_ = Url.objects.filter(long_version=long_version)
        if len(_url_) > 0:
            # permission check
            if _url_.first().user == request.user:
                # data
                _cache_name_count = str(url) + '_visited_count'
                _cache_name = str(url) + '_visited'
                browser_set = set()
                device_set = set()
                ip_set = set()
                _url_clients_cache = cache.get(_cache_name)
                for i in _url_clients_cache:
                    browser_set.update([list(i.values())[0]['user_browser']])
                    device_set.update([list(i.values())[0]['user_device']])
                    ip_set.update([list(i.values())[0]['user_ip']])

                # count data

                # all
                all_count = cache.get(_cache_name_count)

                # browser
                _browser_count = {}
                for i in browser_set:
                    _browser_count.update({i: 0})
                for visit in _url_clients_cache:
                    for browser in browser_set:
                        if browser == list(visit.values())[0]['user_browser']:
                            _browser_count[browser] += 1
                            break

                # device
                _device_count = {}
                for i in device_set:
                    _device_count.update({i: 0})
                for visit in _url_clients_cache:
                    for device in device_set:
                        if device == list(visit.values())[0]['user_device']:
                            _device_count[device] += 1
                            break

                # client data
                ip_device_dict = {}
                ip_browser_dict = {}
                for i in ip_set:
                    for visit in _url_clients_cache:
                        _detail = list(visit.values())[0]
                        if _detail['user_ip'] == i:
                            ip_device_dict.update({i: _detail['user_device']})
                            ip_browser_dict.update({i: _detail['user_browser']})

                # all
                client_all_count = len(ip_set)

                # device
                _ip_device_count = {}
                for i in ip_set:

                    for device in device_set:
                        _count = 0
                        for visit in _url_clients_cache:
                            _detail = list(visit.values())[0]
                            if _detail['user_device'] == device and _detail['user_ip'] == i:
                                _count += 1

                        _ip_device_count.update({i: [{device: _count}] + _ip_device_count.get(i, [])})

                # browser
                _ip_browser_count = {}
                for i in ip_set:

                    for browser in browser_set:
                        _count = 0
                        for visit in _url_clients_cache:
                            _detail = list(visit.values())[0]
                            if _detail['user_browser'] == browser and _detail['user_ip'] == i:
                                _count += 1
                        _ip_browser_count.update({i: [{browser: _count}] + _ip_browser_count.get(i, [])})

                return Response(data={
                    'all': {
                        'all': all_count,
                        'browser': _browser_count,
                        'device': _device_count
                    },
                    'client': {
                        'all': client_all_count,
                        'browser': _ip_browser_count,
                        'device': _ip_device_count
                    }
                },
                    status=status.HTTP_200_OK)

    return Response(status=status.HTTP_404_NOT_FOUND)
