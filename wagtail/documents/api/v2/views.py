from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from wagtail.api.v2.views import BaseAPIViewSet, BaseFieldsConfig

from ... import get_document_model
from .serializers import DocumentSerializer


class DocumentFieldsConfig(BaseFieldsConfig):
    base_serializer_class = DocumentSerializer
    body_fields = BaseFieldsConfig.body_fields + ["title"]
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


class DocumentsAPIViewSet(BaseAPIViewSet):
    base_serializer_class = DocumentSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]

    name = "documents"
    model = get_document_model()
    fields_config_class = DocumentFieldsConfig
