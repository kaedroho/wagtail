from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel, OneToOneRel, RelatedField
from modelcluster.fields import ParentalManyToManyField


class APIField:
    def __init__(self, name, serializer=None):
        self.name = name
        self.serializer = serializer

    def select_on_queryset(self, queryset):
        """
        Override this method to apply prefetch_related or select_related to the given
        QuerySet in order to improve rendering speed of this field on listings.
        """
        try:
            field = queryset.model._meta.get_field(self.name)
        except FieldDoesNotExist:
            return queryset

        if isinstance(field, RelatedField) and not isinstance(field, ParentalManyToManyField):
            if field.many_to_one or field.one_to_one:
                queryset = queryset.select_related(self.field_name)
            elif field.one_to_many or field.many_to_many:
                queryset = queryset.prefetch_related(self.field_name)

        elif isinstance(field, ForeignObjectRel):
            # Reverse relation
            if isinstance(field, OneToOneRel):
                # select_related for reverse OneToOneField
                queryset = queryset.select_related(self.field_name)
            else:
                # prefetch_related for anything else (reverse ForeignKey/ManyToManyField)
                queryset = queryset.prefetch_related(self.field_name)

        return queryset

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<APIField {}>'.format(self.name)
