from ..v2.views import ImageFieldsConfig, ImagesAPIViewSet
from .serializers import AdminImageSerializer


class ImageAdminFieldsConfig(ImageFieldsConfig):
    base_serializer_class = AdminImageSerializer

    body_fields = ImageFieldsConfig.body_fields + [
        "thumbnail",
    ]

    listing_default_fields = ImageFieldsConfig.listing_default_fields + [
        "width",
        "height",
        "thumbnail",
    ]


class ImagesAdminAPIViewSet(ImagesAPIViewSet):
    fields_config_class = ImageAdminFieldsConfig
