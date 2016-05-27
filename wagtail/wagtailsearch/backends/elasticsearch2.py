from wagtail.wagtailsearch.index import FilterField, RelatedFields, SearchField

from .elasticsearch import ElasticsearchSearchBackend, ElasticsearchMapping, ElasticsearchSearchQuery, ElasticsearchSearchResults, ElasticsearchIndex


def get_model_root(model):
    if model._meta.parents:
        return list(model._meta.parents.items())[0][0]

    return model


class Elasticsearch2Mapping(ElasticsearchMapping):
    def get_field_column_name(self, field):
        root_model = get_model_root(self.model)
        definition_model = field.get_definition_model(self.model)

        if definition_model != root_model:
            prefix = definition_model._meta.app_label.lower() + '_' + definition_model.__name__.lower() + '__'
        else:
            prefix = ''

        if isinstance(field, FilterField):
            return prefix + field.get_attname(self.model) + '_filter'
        elif isinstance(field, SearchField):
            return prefix + field.get_attname(self.model)
        elif isinstance(field, RelatedFields):
            return prefix + field.field_name


class Elasticsearch2SearchQuery(ElasticsearchSearchQuery):
    mapping_class = Elasticsearch2Mapping


class Elasticsearch2SearchResults(ElasticsearchSearchResults):
    pass


class Elasticsearch2Index(ElasticsearchIndex):
    pass


class Elasticsearch2SearchBackend(ElasticsearchSearchBackend):
    index_class = Elasticsearch2Index
    query_class = Elasticsearch2SearchQuery
    results_class = Elasticsearch2SearchResults
    mapping_class = Elasticsearch2Mapping

    def get_index_for_model(self, model):
        root_model = get_model_root(model)
        index_suffix = '__' + root_model._meta.app_label.lower() + '_' + root_model.__name__.lower()

        return self.index_class(self, self.index_name + index_suffix)

SearchBackend = Elasticsearch2SearchBackend
