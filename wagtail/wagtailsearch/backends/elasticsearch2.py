from __future__ import absolute_import

import json

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.six.moves.urllib.parse import urlparse
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk

from wagtail.wagtailsearch.index import FilterField, RelatedFields, SearchField, class_is_indexed

from .base import BaseSearch
from .elasticsearch import ElasticSearchIndex, ElasticSearchQuery, ElasticSearchResults, ElasticSearchMapping, ElasticSearchIndexRebuilder


class ElasticSearch2(BaseSearch):
    index_class = ElasticSearchIndex
    query_class = ElasticSearchQuery
    results_class = ElasticSearchResults
    mapping_class = ElasticSearchMapping
    rebuilder_class = ElasticSearchIndexRebuilder

    settings = {
        'settings': {
            'analysis': {
                'analyzer': {
                    'ngram_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'lowercase',
                        'filter': ['asciifolding', 'ngram']
                    },
                    'edgengram_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'lowercase',
                        'filter': ['asciifolding', 'edgengram']
                    }
                },
                'tokenizer': {
                    'ngram_tokenizer': {
                        'type': 'nGram',
                        'min_gram': 3,
                        'max_gram': 15,
                    },
                    'edgengram_tokenizer': {
                        'type': 'edgeNGram',
                        'min_gram': 2,
                        'max_gram': 15,
                        'side': 'front'
                    }
                },
                'filter': {
                    'ngram': {
                        'type': 'nGram',
                        'min_gram': 3,
                        'max_gram': 15
                    },
                    'edgengram': {
                        'type': 'edgeNGram',
                        'min_gram': 1,
                        'max_gram': 15
                    }
                }
            }
        }
    }

    def __init__(self, params):
        super(ElasticSearch2, self).__init__(params)

        # Get settings
        self.hosts = params.pop('HOSTS', None)
        self.index_prefix = params.pop('INDEX_PREFIX', 'wagtail')
        self.timeout = params.pop('TIMEOUT', 10)

        # If HOSTS is not set, convert URLS setting to HOSTS
        es_urls = params.pop('URLS', ['http://localhost:9200'])
        if self.hosts is None:
            self.hosts = []

            for url in es_urls:
                parsed_url = urlparse(url)

                use_ssl = parsed_url.scheme == 'https'
                port = parsed_url.port or (443 if use_ssl else 80)

                http_auth = None
                if parsed_url.username is not None and parsed_url.password is not None:
                    http_auth = (parsed_url.username, parsed_url.password)

                self.hosts.append({
                    'host': parsed_url.hostname,
                    'port': port,
                    'url_prefix': parsed_url.path,
                    'use_ssl': use_ssl,
                    'http_auth': http_auth,
                })

        # Get Elasticsearch interface
        # Any remaining params are passed into the Elasticsearch constructor
        self.es = Elasticsearch(
            hosts=self.hosts,
            timeout=self.timeout,
            **params)

    def get_index(self):
        return self.index_class(self, self.index_name)

    def get_rebuilder(self):
        return self.rebuilder_class(self.get_index())

    def reset_index(self):
        # Use the rebuilder to reset the index
        self.get_rebuilder().reset_index()

    def add_type(self, model):
        self.get_index().add_model(model)

    def refresh_index(self):
        self.get_index().refresh()

    def add(self, obj):
        self.get_index().add_item(obj)

    def add_bulk(self, model, obj_list):
        self.get_index().add_items(model, obj_list)

    def delete(self, obj):
        self.get_index().delete_item(obj)


SearchBackend = ElasticSearch2
