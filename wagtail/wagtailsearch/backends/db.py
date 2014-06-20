import warnings

from django.db import models

from wagtail.wagtailsearch.backends.base import BaseSearch
from wagtail.wagtailsearch.indexed import Indexed


class DBSearch(BaseSearch):
    def __init__(self, params):
        super(DBSearch, self).__init__(params)

    def reset_index(self):
        pass # Not needed

    def add_type(self, model):
        pass # Not needed

    def refresh_index(self):
        pass # Not needed

    def add(self, obj):
        pass # Not needed

    def add_bulk(self, obj_list):
        pass # Not needed

    def delete(self, obj):
        pass # Not needed

    def search(self, query_string, model, fields=None, filters={}, prefetch_related=[]):
        # Get terms
        terms = query_string.split()
        if not terms:
            return model.objects.none()

        # Get fields
        if fields is None:
            fields = [field.field_name for field in model.get_searchable_search_fields()]

        # Start will all objects
        query = model.objects.all()

        # Apply filters
        if filters:
            query = query.filter(**filters)

        # Filter by terms
        for term in terms:
            term_query = models.Q()
            for field_name in fields:
                # Check if the field exists (this will filter out indexed callables)
                try:
                    model._meta.get_field_by_name(field_name)
                except:
                    continue

                # Filter on this field
                term_query |= models.Q(**{'%s__icontains' % field_name: term})

            query = query.filter(term_query)

        # Distinct
        query = query.distinct()

        # Give deprecation warning if prefetch_related was used
        warnings.warn("prefetch_related on search queries is no longer implemented. ", DeprecationWarning)

        return query