from django.contrib.auth.middleware import RemoteUserMiddleware


class HeaderRemoteUserMiddleware(RemoteUserMiddleware):
    header = 'HTTP_AUTHUSER'
