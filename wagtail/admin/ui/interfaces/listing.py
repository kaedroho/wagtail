from .template import TemplateInterface

from wagtail.core.models import TranslatableMixin
from wagtail.search.index import Indexed


class ListingInterface(TemplateInterface):
    template_name = 'wagtailadmin/interfaces/listing.html'

    def __init__(self, columns, queryset):
        self.queryset = queryset
        self.model = queryset.model
        self.columns = [
            BoundColumn(column, self.model)
            for column in columns
        ]
        self.is_searchable = issubclass(self.model, Indexed)
        self.is_translatable = issubclass(self.model, TranslatableMixin)

    def get_context(self, request):
        return {
            'request': request,
            'columns': columns,
            'objects': self.queryset,
            'is_searchable': self.is_searchable,
            'is_translatable': self.is_translatable,
        }


class Column:
    def __init__(self, field_name, heading=None):
        self.field_name = field_name
        self.heading = heading


class BoundColumn:
    def __init__(self, column, model):
        self.field = model._meta.get_field(column.field_name)
        self.heading = column.heading or model._meta.verbose_name.title()

    def get_value(self, object):
        return self.field.value_from_object(object)
