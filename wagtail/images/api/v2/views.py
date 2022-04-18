from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from wagtail.api.v2.views import BaseAPIViewSet

from ... import get_image_model
from .serializers import ImageSerializer


class ImagesAPIViewSet(BaseAPIViewSet):
    base_serializer_class = ImageSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]

    name = "images"
    model = get_image_model()

    class FieldsConfig(BaseAPIViewSet.FieldsConfig):
        base_serializer_class = ImageSerializer

        body_fields = BaseAPIViewSet.FieldsConfig.body_fields + [
            "title",
            "width",
            "height",
        ]
        meta_fields = BaseAPIViewSet.FieldsConfig.meta_fields + ["tags", "download_url"]
        listing_default_fields = BaseAPIViewSet.FieldsConfig.listing_default_fields + [
            "title",
            "tags",
            "download_url",
        ]
        nested_default_fields = BaseAPIViewSet.FieldsConfig.nested_default_fields + [
            "title",
            "download_url",
        ]
