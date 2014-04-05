from django.db import models
from django.conf import settings

from elasticutils import get_es, S, F

from wagtail.wagtailsearch.backends.base import BaseSearch
from wagtail.wagtailsearch.indexed import Indexed

import string


class ElasticSearchResultsSet(object):
    def __init__(self, backend, query_set, query_string, fields):
        self.backend = backend
        self.query_set = query_set
        self.query_string = query_string
        self.fields = fields

    def _get_filters(self, node):
        # Check if this is a leaf node
        if isinstance(node, tuple):
            col = node[0].col
            lookup_type = node[1]
            value = node[3]

            if lookup_type != 'exact':
                return F(**{col + '__' + lookup_type: value})
            else:
                return F(**{col: value})

        # Get child filters
        connector = node.connector
        child_filters = [self._get_filters(child) for child in node.children]

        # Connect them
        if child_filters:
            filters_connected = child_filters[0]
            for extra_filter in child_filters[1:]:
                if connector == 'AND':
                    filters_connected &= extra_filter
                elif connector == 'OR':
                    filters_connected |= extra_filter
                else:
                    raise Exception("Unknown connector: " + connector)

            return filters_connected
        else:
            return F()

    def get_filters(self):
        query_set_filters = self._get_filters(self.query_set.query.where)
        content_type_filter = F(content_type__prefix=self.query_set.model.indexed_get_content_type())
        return query_set_filters & content_type_filter

    @property
    def query(self):
        # Start query
        query = self.backend.s.query_raw({
            'query_string': {
                'query': self.query_string,
                'fields': self.fields,
            }
        })

        # Apply filters
        query = query.filter(self.get_filters())

        return query

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Get primary keys
            pk_list_unclean = [result._source["pk"] for result in self.query[key]]

            # Remove duplicate keys (and preserve order)
            seen_pks = set()
            pk_list = []
            for pk in pk_list_unclean:
                if pk not in seen_pks:
                    seen_pks.add(pk)
                    pk_list.append(pk)

            # Get results
            results = self.query_set.filter(pk__in=pk_list)

            # Put results into a dictionary (using primary key as the key)
            results_dict = {str(result.pk): result for result in results}

            # Build new list with items in the correct order
            results_sorted = [results_dict[str(pk)] for pk in pk_list if str(pk) in results_dict]

            # Return the list
            return results_sorted
        else:
            # Return a single item
            pk = self.query[key]._source["pk"]
            return self.query_set.get(pk=pk)

    def __len__(self):
        return self.query.count()

    def count(self):
        return len(self)

    def exists(self):
        return bool(len(self))

    def filter(self, *args, **kwargs):
        return ElasticSearchResultsSet(
            self.backend,
            self.query_set.filter(*args, **kwargs),
            self.query_string,
            self.fields
        )

    def exclude(self, *args, **kwargs):
        return ElasticSearchResultsSet(
            self.backend,
            self.query_set.exclude(*args, **kwargs),
            self.query_string,
            self.fields
        )

    def prefetch_related(self, *args, **kwargs):
        return ElasticSearchResultsSet(
            self.backend,
            self.query_set.prefetch_related(*args, **kwargs),
            self.query_string,
            self.fields
        )


class ElasticSearch(BaseSearch):
    def __init__(self, params):
        super(ElasticSearch, self).__init__(params)

        # Get settings
        self.es_urls = params.get('URLS', ['http://localhost:9200'])
        self.es_index = params.get('INDEX', 'wagtail')

        # Get ElasticSearch interface
        self.es = get_es(urls=self.es_urls)
        self.s = S().es(urls=self.es_urls).indexes(self.es_index)

    def reset_index(self):
        # Delete old index
        try:
            self.es.delete_index(self.es_index)
        except:
            pass

        # Settings
        INDEX_SETTINGS = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "lowercase",
                            "filter": ["ngram"]
                        },
                        "edgengram_analyzer": {
                            "type": "custom",
                            "tokenizer": "lowercase",
                            "filter": ["edgengram"]
                        }
                    },
                    "tokenizer": {
                        "ngram_tokenizer": {
                            "type": "nGram",
                            "min_gram": 3,
                            "max_gram": 15,
                        },
                        "edgengram_tokenizer": {
                            "type": "edgeNGram",
                            "min_gram": 2,
                            "max_gram": 15,
                            "side": "front"
                        }
                    },
                    "filter": {
                        "ngram": {
                            "type": "nGram",
                            "min_gram": 3,
                            "max_gram": 15
                        },
                        "edgengram": {
                            "type": "edgeNGram",
                            "min_gram": 1,
                            "max_gram": 15
                        }
                    }
                }
            }
        }

        # Create new index
        self.es.create_index(self.es_index, INDEX_SETTINGS)

    def add_type(self, model):
        # Get type name
        content_type = model.indexed_get_content_type()

        # Make field list
        fields = dict({
            "pk": dict(type="string", index="not_analyzed", store="yes"),
            "content_type": dict(type="string"),
        }.items())

        # Add indexed fields
        for field_name, config in model.indexed_get_search_fields().items():
            if config is not None:
                fields[field_name] = config
            else:
                fields[field_name] = dict(
                    type='string',
                    index='not_analyzed',
                )

        # Put mapping
        self.es.put_mapping(self.es_index, content_type, {
            content_type: {
                "properties": fields,
            }
        })

    def refresh_index(self):
        self.es.refresh(self.es_index)

    def add(self, obj):
        # Make sure the object can be indexed
        if not self.object_can_be_indexed(obj):
            return

        # Build document
        doc = obj.indexed_build_document()

        # Add to index
        self.es.index(self.es_index, obj.indexed_get_content_type(), doc, id=doc["id"])

    def add_bulk(self, obj_list):
        # Group all objects by their type
        type_set = {}
        for obj in obj_list:
            # Object must be a decendant of Indexed and be a django model
            if not self.object_can_be_indexed(obj):
                continue

            # Get object type
            obj_type = obj.indexed_get_content_type()

            # If type is currently not in set, add it
            if obj_type not in type_set:
                type_set[obj_type] = []

            # Add object to set
            type_set[obj_type].append(obj.indexed_build_document())

        # Loop through each type and bulk add them
        results = []
        for type_name, type_objects in type_set.items():
            results.append((type_name, len(type_objects)))
            self.es.bulk_index(self.es_index, type_name, type_objects)
        return results

    def delete(self, obj):
        # Object must be a decendant of Indexed and be a django model
        if not isinstance(obj, Indexed) or not isinstance(obj, models.Model):
            return

        # Get ID for document
        doc_id = obj.indexed_get_document_id()

        # Delete document
        try:
            self.es.delete(self.es_index, obj.indexed_get_content_type(), doc_id)
        except:
            pass  # Document doesn't exist, ignore this exception

    def search(self, query_set, query_string, fields=None):
        # Model must be a descendant of Indexed and be a django model
        if not issubclass(query_set.model, Indexed) or not issubclass(query_set.model, models.Model):
            return query_set.none()

        # Clean up query string
        query_string = "".join([c for c in query_string if c not in string.punctuation])

        # Check that theres still a query string after the clean up
        if not query_string:
            return query_set.none()

        # Get fields
        field_config = query_set.model.indexed_get_search_fields()
        if fields is None:
            fields = [name for name, config in field_config.items() if config and config['type'] == 'string' and config['boost']]

        # Return search results
        return ElasticSearchResultsSet(self, query_set, query_string, fields)
