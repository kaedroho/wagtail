from __future__ import absolute_import, unicode_literals

from .elasticsearch import (
    ElasticsearchIndex, ElasticsearchMapping, ElasticsearchSearchBackend, ElasticsearchSearchQuery,
    ElasticsearchSearchResults)


def get_model_root(model):
    """
    This function finds the root model for any given model. The root model is
    the highest concrete model that it descends from. If the model doesn't
    descend from another concrete model then the model is it's own root model so
    it is returned.

    Examples:
    >>> get_model_root(wagtailcore.Page)
    wagtailcore.Page

    >>> get_model_root(myapp.HomePage)
    wagtailcore.Page

    >>> get_model_root(wagtailimages.Image)
    wagtailimages.Image
    """
    if model._meta.parents:
        return list(model._meta.parents.items())[0][0]

    return model


class Elasticsearch2Mapping(ElasticsearchMapping):
    pass


class Elasticsearch2Index(ElasticsearchIndex):
    pass


class Elasticsearch2SearchQuery(ElasticsearchSearchQuery):
    mapping_class = Elasticsearch2Mapping


class Elasticsearch2SearchResults(ElasticsearchSearchResults):
    pass


class Elasticsearch2SearchBackend(ElasticsearchSearchBackend):
    mapping_class = Elasticsearch2Mapping
    index_class = Elasticsearch2Index
    query_class = Elasticsearch2SearchQuery
    results_class = Elasticsearch2SearchResults

    def get_index_for_model(self, model):
        root_model = get_model_root(model)
        index_suffix = '__' + root_model._meta.app_label.lower() + '_' + root_model.__name__.lower()

        return self.index_class(self, self.index_name + index_suffix)


SearchBackend = Elasticsearch2SearchBackend
