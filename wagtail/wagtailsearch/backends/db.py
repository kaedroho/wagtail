from __future__ import absolute_import, unicode_literals

import warnings
from functools import reduce
from operator import and_, or_

from django.db import models

from wagtail.utils.deprecation import RemovedInWagtail18Warning
from wagtail.wagtailsearch.backends.base import (
    BaseSearchBackend, BaseSearchResults)
from wagtail.wagtailsearch.query import (
    MatchQuery, TermQuery, PrefixQuery, RangeQuery, MatchAllQuery, MatchNoneQuery, AndQuery, OrQuery, FilterQuery)


class DatabaseSearchResults(BaseSearchResults):
    def query_to_queryset(self, query):
        if isinstance(query, MatchQuery):
            # Get fields
            model = self.queryset.model
            fields = query.fields or [field.field_name for field in model.get_searchable_search_fields()]

            # Get terms
            terms = query.query_string.split()
            if not terms:
                return self.queryset.none()

            q = models.Q()

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

                if query.operator == 'or':
                    q |= term_query
                else:
                    q &= term_query

            return self.queryset.filter(q)

        elif isinstance(query, TermQuery):
            return self.queryset.filter(**{query.field: query.value})

        elif isinstance(query, PrefixQuery):
            return self.queryset.filter(**{'%s__startswith' % query.field: query.prefix})

        elif isinstance(query, RangeQuery):
            pass  # TODO

        elif isinstance(query, MatchAllQuery):
            return self.queryset.all()

        elif isinstance(query, MatchNoneQuery):
            return self.queryset.none()

        elif isinstance(query, AndQuery):
            return reduce(and_, [self.query_to_queryset(query) for query in query.subqueries])

        elif isinstance(query, OrQuery):
            return reduce(or_, [self.query_to_queryset(query) for query in query.subqueries])

        elif isinstance(query, FilterQuery):
            qs = self.query_to_queryset(query.query)

            if query.include:
                qs &= self.query_to_queryset(query.include)

            if query.exclude:
                qs &= ~self.query_to_queryset(query.include)

            return qs

        raise

    def get_queryset(self):
        return self.query_to_queryset(self.query.rewrite()).distinct()[self.start:self.stop]

    def _do_search(self):
        return self.get_queryset()

    def _do_count(self):
        return self.get_queryset().count()


class DatabaseSearchBackend(BaseSearchBackend):
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
