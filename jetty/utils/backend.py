import requests

from jetty import settings
from jetty.models.token import Token


def api_method_url(method):
    return '{}/{}'.format(settings.JETTY_BACKEND_API_BASE_URL, method)


def register_token():
    token = Token.objects.all().first()

    if token:
        return token, False

    url = api_method_url('project_tokens/')
    headers = {
        'User-Agent': 'Jetty Django'
    }

    r = requests.request('POST', url, headers=headers)

    if r.status_code != 200:
        return None, False

    result = r.json()
    token = Token.objects.create(token=result['token'], date_add=result['date_add'])

    return token, True


def project_auth(token):
    project_token = Token.objects.all().first()

    if not project_token:
        return False

    url = api_method_url('project_auth/')
    data = {
        'project_token': project_token.token,
        'token': token
    }
    headers = {
        'User-Agent': 'Jetty Django'
    }

    r = requests.request('POST', url, data=data, headers=headers)

    print('auth', r.status_code)
    return r.status_code == 200