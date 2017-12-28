import json
import logging
import requests
import sys
import pytz
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if len(logger.handlers) == 0:
    # logger.handlers.append(logging.NullHandler())
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    logger.handlers.append(console)


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class DbApi(object):
    """
    Instant an object read and call it
    __api_type: like "/meta/camp"
    __retry: retrycount
    __sleep: sleep seconds before retry
    kwargs: api paramaters
    Reference: http://git.tianrang-inc.com/newR/retailer-report-server/wikis/Rest-API-v1

    e.g.:
            reader = DbReader('http://172.18.130.2:8080')
            reader(
    """

    def __init__(self, url_header, token=None, version=1):
        if token:
            self.api = url_header + '/api/v{}'.format(version)
        else:
            self.api = url_header
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': token})

    def get(self, __api_type, **kwargs):
        for key, val in kwargs.items():
            if isinstance(val, list):
                kwargs[key] = json.dumps(val)

        try:
            response = requests_retry_session(session=self.session).get(self.api + __api_type, params=kwargs,
                                                                        timeout=60)
        except Exception as e:
            raise sys.exc_type("Request fail url {}, params {}, message {}"
                               .format(self.api + __api_type, kwargs, e))
        data, status_code = process_response(response)
        return data if data else status_code

    def post(self, __api_type, __post_obj):
        try:
            response = requests_retry_session(session=self.session).post(self.api + __api_type, json=__post_obj)
        except Exception as e:
            raise sys.exc_type("Request fail url {}, message {}".format(self.api + __api_type, e))
        data, status_code = process_response(response)
        return data if data else status_code


def get_token(url, user="admin", pw="admin123"):
    db_api = DbApi(url)
    return db_api.post("/api-token-auth/", {"username": user, "password": pw})['token']


class DbReadError(Exception):
    def __init__(self, e):
        Exception(self)
        self.expression = e

    def __str__(self):
        return self.expression


def process_response(response):
    if response.ok:
        result = response.json()
        if not isinstance(result, dict):
            try:
                result = json.loads(result)
            except ValueError:
                return None, response.status_code
        return result, response.status_code
    else:
        return None, response.status_code


if __name__ == '__main__':
    url = 'http://172.18.130.101:8080'
    token = get_token(url)
    print(token)
    db_api = DbApi(url, token)

    area_id = None
    for item in db_api.get('/cameras/')['results']:
        area_id = item['rects'][0]['area']
        print(item)
        break
    if area_id:
        time_str = datetime.now(tz=pytz.UTC).isoformat()
        print(db_api.post('/log/people/', {'gender': 1, 'age': 25, 'area': area_id, 'time': time_str}))
