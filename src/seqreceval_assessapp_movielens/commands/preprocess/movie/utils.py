import functools
import urllib.parse
import time

import requests


class Scheduler:
    @property
    def until(self):
        if not self._last:
            return 0

        elapsed = self._now - self._last

        return max(self.interval - elapsed, 0)

    @property
    def _now(self):
        return time.time()

    def __init__(self, interval):
        self.interval = interval
        self._last = None

    def execute(self, f, *args, **kwargs):
        until = self.until

        if until > 0:
            time.sleep(until)

        output = f(*args, **kwargs)

        self._last = self._now

        return output

    def schedule(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return self.execute(f, *args, **kwargs)

        return wrapper


class MovieLensAPI:
    BASE_URL = "https://movielens.org/api/"
    _scheduler = Scheduler(0)

    def __init__(self, username, password, interval=0):
        self._session = requests.Session()
        self._scheduler.interval = interval
        self._login(username, password)

    def _endpoint(self, resource):
        return urllib.parse.urljoin(self.BASE_URL, resource)

    @_scheduler.schedule
    def _login(self, username, password):
        res = self._session.post(self._endpoint("sessions"), json={"userName": username, "password": password})
        res.raise_for_status()

    @_scheduler.schedule
    def _logout(self):
        res = self._session.delete(self._endpoint("sessions/me"))
        res.raise_for_status()

    @_scheduler.schedule
    def movie(self, id_):
        res = self._session.get(self._endpoint(f"movies/{id_}"))
        res.raise_for_status()

        return res.json()["data"]["movieDetails"]["movie"]


class TheMovieDatabaseAPI:
    BASE_URL = "https://api.themoviedb.org/3/"
    _scheduler = Scheduler(0)

    def __init__(self, access_token, language="en-US", interval=0):
        self._session = requests.Session()
        self._session.headers.update(self._headers(access_token))
        self._language = language
        self._scheduler.interval = interval

    def _headers(self, token):
        return {"Authorization": f"Bearer {token}"}

    def _endpoint(self, resource):
        return urllib.parse.urljoin(self.BASE_URL, resource)

    @_scheduler.schedule
    def movie(self, id_):
        res = self._session.get(self._endpoint(f"movie/{id_}"), params={"language": self._language})
        res.raise_for_status()

        return res.json()
