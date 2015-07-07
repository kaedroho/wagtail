from django.db.models.query import QuerySet

from wagtail.wagtailsearch.backends import get_search_backend


class SearchableQuerySetMixin(object):
    def search(self, query_string, fields=None, backend='default'):
        """
        This runs a search query on all the images in the QuerySet
        """
        search_backend = get_search_backend(backend)
        return search_backend.search(query_string, self, fields=fields)


class SearchableQuerySet(SearchableQuerySetMixin, QuerySet):
    pass
