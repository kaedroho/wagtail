from django.urls import re_path

from wagtail.videos.views.serve import serve

urlpatterns = [
    re_path(r"^([^/]*)/(\d*)/([^/]*)/[^/]*$", serve, name="wagtailvideos_serve"),
]
