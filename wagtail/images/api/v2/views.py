from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from wagtail.api.v2.views import BaseAPIViewSet, BaseFieldsConfig

from ... import get_image_model
from .serializers import ImageSerializer


class ImageFieldsConfig(BaseFieldsConfig):
    base_serializer_class = ImageSerializer

    body_fields = BaseFieldsConfig.body_fields + [
        "title",
        "width",
        "height",
    ]
    meta_fields = BaseFieldsConfig.meta_fields + ["tags", "download_url"]
    listing_default_fields = BaseFieldsConfig.listing_default_fields + [
        "title",
        "tags",
        "download_url",
    ]
    nested_default_fields = BaseFieldsConfig.nested_default_fields + [
        "title",
        "download_url",
    ]


class ImagesAPIViewSet(BaseAPIViewSet):
    base_serializer_class = ImageSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]

    name = "images"
    model = get_image_model()
    fields_config_class = ImageFieldsConfig
