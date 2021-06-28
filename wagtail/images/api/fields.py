from collections import OrderedDict

from django.db import models
from rest_framework.fields import Field

from wagtail.api.conf import APIField
from ..models import SourceImageIOError


class ImageRenditionField(Field):
    """
    A field that generates a rendition with the specified filter spec, and serialises
    details of that rendition.

    Example:
    "thumbnail": {
        "url": "/media/images/myimage.max-165x165.jpg",
        "width": 165,
        "height": 100,
        "alt": "Image alt text"
    }

    If there is an error with the source image. The dict will only contain a single
    key, "error", indicating this error:

    "thumbnail": {
        "error": "SourceImageIOError"
    }
    """
    def __init__(self, filter_spec, *args, **kwargs):
        self.filter_spec = filter_spec
        super().__init__(*args, **kwargs)

    def to_representation(self, image):
        try:
            thumbnail = image.get_rendition(self.filter_spec)

            return OrderedDict([
                ('url', thumbnail.url),
                ('width', thumbnail.width),
                ('height', thumbnail.height),
                ('alt', thumbnail.alt),
            ])
        except SourceImageIOError:
            return OrderedDict([
                ('error', 'SourceImageIOError'),
            ])


class ImageRenditionAPIField(APIField):
    def __init__(self, name, filter_spec, *args, **kwargs):
        super().__init__(name, serializer=ImageRenditionField(filter_spec, *args, **kwargs))
        self.filter_spec = filter_spec

    def select_on_queryset(self, queryset):
        queryset = super().select_on_queryset(queryset)
        image_field = queryset.model._meta.get_field(self.name)
        image_model = image_field.related_model
        rendition_model = image_model.get_rendition_model()

        return queryset.prefetch_related(
            models.Prefetch(
                self.name + '__renditions',
                queryset=rendition_model.objects.filter(filter_spec=self.filter_spec),
                to_attr='prefetched_renditions'
            )
        )
