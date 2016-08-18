from __future__ import absolute_import, unicode_literals

from django.contrib.auth.middleware import RemoteUserMiddleware


class HeaderRemoteUserMiddleware(RemoteUserMiddleware):
    header = 'HTTP_AUTHUSER'
