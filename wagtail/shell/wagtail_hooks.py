from django.urls import path

from wagtail.core import hooks

from . import views


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('shell/', views.shell),
    ]
