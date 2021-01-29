import string
import random
from django.core.cache import cache


def short_random_string():
    n = 5
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(n))


def make_shorten(re_path=None, try_slug=''):
    _return = None
    if re_path is None:
        _return = short_random_string()
    else:
        _return = re_path
    if try_slug:
        return _return + str(try_slug)
    return _return


def check_uniq(short_version):
    _url = cache.get(short_version, None)
    if _url is None:
        return True
    return False
