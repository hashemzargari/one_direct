import random
from locust import HttpUser, between, task

short_codes = []
URL_LIST = ['https://requests.readthedocs.io/en/latest/_modules/requests/models/#Response',
            'http://127.0.0.1:8000/api/v1/urls/create/',
            'http://localhost/worker/celery',
            'elearn.ut.ac.ir']
RE_PATH_LIST = [None, 'hashem', 'zargari', 'digi', 'nasa', None, 'personal']


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    def on_start(self):
        self.client.post("/api-auth/login/", {
            "username": "admin",
            "password": "admin"
        })

    @task
    def create_short_url(self):
        res = self.client.post('/api/v1/urls/create/',
                               data={'long_version': random.choice(URL_LIST),
                                     're_path': random.choice(RE_PATH_LIST)})
        short_codes.append(res.text)

    @task
    def redirest_url(self):
        if len(short_codes) > 0:
            self.client.get(f"/r/{random.choice(short_codes)}")


# to run benchmarking -> locust -f locustfile.py