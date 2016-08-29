from __future__ import absolute_import, unicode_literals

import warnings

from django.db import models

from wagtail.utils.deprecation import RemovedInWagtail18Warning
from wagtail.wagtailsearch.backends.base import (
    BaseSearchBackend, BaseSearchQuery, BaseSearchResults)


class DatabaseSearchQuery(BaseSearchQuery):
    def _process_lookup(self, field, lookup, value):
        return models.Q(**{field.get_attname(self.queryset.model) + '__' + lookup: value})

    def _connect_filters(self, filters, connector, negated):
        if connector == 'AND':
            q = models.Q(*filters)
        elif connector == 'OR':
            q = models.Q(filters[0])
            for fil in filters[1:]:
                q |= fil
        else:
            return

        if negated:
            q = ~q

        return q

    def get_extra_q(self):
        q = models.Q()
        model = self.queryset.model

        return q

        if self.query_string is not None:
            # Get fields
            fields = self.fields or [field.field_name for field in model.get_searchable_search_fields()]

            # Get terms
            terms = self.query_string.split()
            if not terms:
                return model.objects.none()

            # Filter by terms
            for term in terms:
                term_query = models.Q()
                for field_name in fields:
                    # Check if the field exists (this will filter out indexed callables)
                    try:
                        model._meta.get_field(field_name)
                    except models.fields.FieldDoesNotExist:
                        continue

                    # Filter on this field
                    term_query |= models.Q(**{'%s__icontains' % field_name: term})

                if self.operator == 'or':
                    q |= term_query
                elif self.operator == 'and':
                    q &= term_query

        return q


class DatabaseSearchResults(BaseSearchResults):
    def get_queryset(self):
        queryset = self.query.queryset
        q = self.query.get_extra_q()

        return queryset.filter(q).distinct()[self.start:self.stop]

    def _do_search(self):
        return self.get_queryset()

    def _do_count(self):
        return self.get_queryset().count()


class DatabaseSearchBackend(BaseSearchBackend):
    DEFAULT_OPERATOR = 'and'

    query_class = DatabaseSearchQuery
    results_class = DatabaseSearchResults

    def __init__(self, params):
        super(DatabaseSearchBackend, self).__init__(params)

    def reset_index(self):
        pass  # Not needed

    def add_type(self, model):
        pass  # Not needed

    def refresh_index(self):
        pass  # Not needed

    def add(self, obj):
        pass  # Not needed

    def add_bulk(self, model, obj_list):
        return  # Not needed

    def delete(self, obj):
        pass  # Not needed



class DBSearch(DatabaseSearchBackend):
    def __init__(self, params):
        warnings.warn(
            "The wagtail.wagtailsearch.backends.db.DBSearch has "
            "been moved to wagtail.wagtailsearch.backends.db.DatabaseSearchBackend",
            category=RemovedInWagtail18Warning, stacklevel=2
        )

        super(DBSearch, self).__init__(params)


SearchBackend = DatabaseSearchBackend
