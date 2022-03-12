from ..v2.views import VideosAPIViewSet
from .serializers import AdminVideoSerializer


class VideosAdminAPIViewSet(VideosAPIViewSet):
    base_serializer_class = AdminVideoSerializer

    body_fields = VideosAPIViewSet.body_fields + [
        "thumbnail",
    ]

    listing_default_fields = VideosAPIViewSet.listing_default_fields + [
        "width",
        "height",
        "thumbnail",
    ]
