from django.conf import settings
from django.contrib import admin

from wagtail.videos.models import Video

if (
    hasattr(settings, "WAGTAILIMAGES_IMAGE_MODEL")
    and settings.WAGTAILIMAGES_IMAGE_MODEL != "wagtailvideos.Video"
):
    # This installation provides its own custom video class;
    # to avoid confusion, we won't expose the unused wagtailvideos.Video class
    # in the admin.
    pass
else:
    admin.site.register(Video)
