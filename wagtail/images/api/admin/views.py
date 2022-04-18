from ..v2.views import ImagesAPIViewSet
from .serializers import AdminImageSerializer


class ImagesAdminAPIViewSet(ImagesAPIViewSet):
    class FieldsConfig(ImagesAPIViewSet.FieldsConfig):
        base_serializer_class = AdminImageSerializer

        body_fields = ImagesAPIViewSet.FieldsConfig.body_fields + [
            "thumbnail",
        ]

        listing_default_fields = (
            ImagesAPIViewSet.FieldsConfig.listing_default_fields
            + [
                "width",
                "height",
                "thumbnail",
            ]
        )
