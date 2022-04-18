from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from wagtail.api.v2.views import BaseAPIViewSet

from ... import get_document_model
from .serializers import DocumentSerializer


class DocumentsAPIViewSet(BaseAPIViewSet):
    base_serializer_class = DocumentSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]

    name = "documents"
    model = get_document_model()

    class FieldsConfig(BaseAPIViewSet.FieldsConfig):
        base_serializer_class = DocumentSerializer
        body_fields = BaseAPIViewSet.FieldsConfig.body_fields + ["title"]
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
