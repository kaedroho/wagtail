# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import os
import unittest

import mock
from django.db.models import Q
from django.test import TestCase
from elasticsearch.serializer import JSONSerializer

from wagtail.tests.search import models
from wagtail.wagtailsearch.backends import get_search_backend
from wagtail.wagtailsearch.backends.elasticsearch2 import ElasticSearch2

from .test_elasticsearch_backend import TestElasticSearchBackend


class TestElasticSearch2Backend(TestElasticSearchBackend):
    backend_path = 'wagtail.wagtailsearch.backends.elasticsearch2'


class TestElasticSearchMapping(TestCase):
    def assertDictEqual(self, a, b):
        default = JSONSerializer().default
        self.assertEqual(
            json.dumps(a, sort_keys=True, default=default), json.dumps(b, sort_keys=True, default=default)
        )

    def setUp(self):
        # Create ES mapping
        self.es_mapping = ElasticSearch2.mapping_class(models.SearchTest)

        # Create ES document
        self.obj = models.SearchTest(title="Hello")
        self.obj.save()
        self.obj.tags.add("a tag")

    def test_get_document_type(self):
        self.assertEqual(self.es_mapping.get_document_type(), 'searchtests_searchtest')

    def test_get_mapping(self):
        # Build mapping
        mapping = self.es_mapping.get_mapping()

        # Check
        expected_result = {
            'searchtests_searchtest': {
                'properties': {
                    'pk': {'index': 'not_analyzed', 'type': 'string', 'store': 'yes', 'include_in_all': False},
                    'content_type': {'index': 'not_analyzed', 'type': 'string', 'include_in_all': False},
                    '_partials': {'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default', 'include_in_all': False, 'type': 'string'},
                    'live_filter': {'index': 'not_analyzed', 'type': 'boolean', 'include_in_all': False},
                    'published_date_filter': {'index': 'not_analyzed', 'type': 'date', 'include_in_all': False},
                    'title': {'type': 'string', 'include_in_all': True, 'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default'},
                    'title_filter': {'index': 'not_analyzed', 'type': 'string', 'include_in_all': False},
                    'content': {'type': 'string', 'include_in_all': True},
                    'callable_indexed_field': {'type': 'string', 'include_in_all': True},
                    'tags': {
                        'type': 'nested',
                        'properties': {
                            'name': {'type': 'string', 'include_in_all': True, 'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default'},
                            'slug_filter': {'index': 'not_analyzed', 'type': 'string', 'include_in_all': False},
                        }
                    },
                }
            }
        }

        self.assertDictEqual(mapping, expected_result)

    def test_get_document_id(self):
        self.assertEqual(self.es_mapping.get_document_id(self.obj), 'searchtests_searchtest:' + str(self.obj.pk))

    def test_get_document(self):
        # Get document
        document = self.es_mapping.get_document(self.obj)

        # Sort partials
        if '_partials' in document:
            document['_partials'].sort()

        # Check
        expected_result = {
            'pk': str(self.obj.pk),
            'content_type': 'searchtests_searchtest',
            '_partials': ['Hello', 'a tag'],
            'live_filter': False,
            'published_date_filter': None,
            'title': 'Hello',
            'title_filter': 'Hello',
            'callable_indexed_field': 'Callable',
            'content': '',
            'tags': [
                {
                    'name': 'a tag',
                    'slug_filter': 'a-tag',
                }
            ],
        }

        self.assertDictEqual(document, expected_result)


class TestElasticSearchMappingInheritance(TestCase):
    def assertDictEqual(self, a, b):
        default = JSONSerializer().default
        self.assertEqual(
            json.dumps(a, sort_keys=True, default=default), json.dumps(b, sort_keys=True, default=default)
        )

    def setUp(self):
        # Create ES mapping
        self.es_mapping = ElasticSearch2.mapping_class(models.SearchTestChild)

        # Create ES document
        self.obj = models.SearchTestChild(title="Hello", subtitle="World", page_id=1)
        self.obj.save()
        self.obj.tags.add("a tag")

    def test_get_document_type(self):
        self.assertEqual(self.es_mapping.get_document_type(), 'searchtests_searchtest_searchtests_searchtestchild')

    def test_get_mapping(self):
        # Build mapping
        mapping = self.es_mapping.get_mapping()

        # Check
        expected_result = {
            'searchtests_searchtest_searchtests_searchtestchild': {
                'properties': {
                    # New
                    'extra_content': {'type': 'string', 'include_in_all': True},
                    'subtitle': {'type': 'string', 'include_in_all': True, 'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default'},
                    'page': {
                        'type': 'nested',
                        'properties': {
                            'title': {'type': 'string', 'include_in_all': True, 'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default'},
                            'search_description': {'type': 'string', 'include_in_all': True},
                            'live_filter': {'index': 'not_analyzed', 'type': 'boolean', 'include_in_all': False},
                        }
                    },

                    # Inherited
                    'pk': {'index': 'not_analyzed', 'type': 'string', 'store': 'yes', 'include_in_all': False},
                    'content_type': {'index': 'not_analyzed', 'type': 'string', 'include_in_all': False},
                    '_partials': {'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default', 'include_in_all': False, 'type': 'string'},
                    'live_filter': {'index': 'not_analyzed', 'type': 'boolean', 'include_in_all': False},
                    'published_date_filter': {'index': 'not_analyzed', 'type': 'date', 'include_in_all': False},
                    'title': {'type': 'string', 'include_in_all': True, 'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default'},
                    'title_filter': {'index': 'not_analyzed', 'type': 'string', 'include_in_all': False},
                    'content': {'type': 'string', 'include_in_all': True},
                    'callable_indexed_field': {'type': 'string', 'include_in_all': True},
                    'tags': {
                        'type': 'nested',
                        'properties': {
                            'name': {'type': 'string', 'include_in_all': True, 'analyzer': 'edgengram_analyzer', 'search_analyzer': 'default'},
                            'slug_filter': {'index': 'not_analyzed', 'type': 'string', 'include_in_all': False},
                        }
                    },
                }
            }
        }

        self.assertDictEqual(mapping, expected_result)

    def test_get_document_id(self):
        # This must be tests_searchtest instead of 'tests_searchtest_tests_searchtestchild'
        # as it uses the contents base content type name.
        # This prevents the same object being accidentally indexed twice.
        self.assertEqual(self.es_mapping.get_document_id(self.obj), 'searchtests_searchtest:' + str(self.obj.pk))

    def test_get_document(self):
        # Build document
        document = self.es_mapping.get_document(self.obj)

        # Sort partials
        if '_partials' in document:
            document['_partials'].sort()

        # Check
        expected_result = {
            # New
            'extra_content': '',
            'subtitle': 'World',
            'page': {
                'title': 'Root',
                'search_description': '',
                'live_filter': True,
            },

            # Changed
            'content_type': 'searchtests_searchtest_searchtests_searchtestchild',

            # Inherited
            'pk': str(self.obj.pk),
            '_partials': ['Hello', 'Root', 'World', 'a tag'],
            'live_filter': False,
            'published_date_filter': None,
            'title': 'Hello',
            'title_filter': 'Hello',
            'callable_indexed_field': 'Callable',
            'content': '',
            'tags': [
                {
                    'name': 'a tag',
                    'slug_filter': 'a-tag',
                }
            ],
        }

        self.assertDictEqual(document, expected_result)


class TestBackendConfiguration(TestCase):
    def test_default_settings(self):
        backend = ElasticSearch2(params={})

        self.assertEqual(len(backend.hosts), 1)
        self.assertEqual(backend.hosts[0]['host'], 'localhost')
        self.assertEqual(backend.hosts[0]['port'], 9200)
        self.assertEqual(backend.hosts[0]['use_ssl'], False)

    def test_hosts(self):
        # This tests that HOSTS goes to es_hosts
        backend = ElasticSearch2(params={
            'HOSTS': [
                {
                    'host': '127.0.0.1',
                    'port': 9300,
                    'use_ssl': True,
                }
            ]
        })

        self.assertEqual(len(backend.hosts), 1)
        self.assertEqual(backend.hosts[0]['host'], '127.0.0.1')
        self.assertEqual(backend.hosts[0]['port'], 9300)
        self.assertEqual(backend.hosts[0]['use_ssl'], True)

    def test_urls(self):
        # This test backwards compatibility with old URLS setting
        backend = ElasticSearch2(params={
            'URLS': [
                'http://localhost:12345',
                'https://127.0.0.1:54321',
                'http://username:password@elasticsearch.mysite.com',
                'https://elasticsearch.mysite.com/hello',
            ],
        })

        self.assertEqual(len(backend.hosts), 4)
        self.assertEqual(backend.hosts[0]['host'], 'localhost')
        self.assertEqual(backend.hosts[0]['port'], 12345)
        self.assertEqual(backend.hosts[0]['use_ssl'], False)

        self.assertEqual(backend.hosts[1]['host'], '127.0.0.1')
        self.assertEqual(backend.hosts[1]['port'], 54321)
        self.assertEqual(backend.hosts[1]['use_ssl'], True)

        self.assertEqual(backend.hosts[2]['host'], 'elasticsearch.mysite.com')
        self.assertEqual(backend.hosts[2]['port'], 80)
        self.assertEqual(backend.hosts[2]['use_ssl'], False)
        self.assertEqual(backend.hosts[2]['http_auth'], ('username', 'password'))

        self.assertEqual(backend.hosts[3]['host'], 'elasticsearch.mysite.com')
        self.assertEqual(backend.hosts[3]['port'], 443)
        self.assertEqual(backend.hosts[3]['use_ssl'], True)
        self.assertEqual(backend.hosts[3]['url_prefix'], '/hello')


@unittest.skipUnless(os.environ.get('ELASTICSEARCH2_URL', False), "ELASTICSEARCH2_URL not set")
class TestRebuilder(TestCase):
    def assertDictEqual(self, a, b):
        default = JSONSerializer().default
        self.assertEqual(
            json.dumps(a, sort_keys=True, default=default), json.dumps(b, sort_keys=True, default=default)
        )

    def setUp(self):
        self.backend = get_search_backend('elasticsearch2')
        self.es = self.backend.es
        self.rebuilder = self.backend.get_rebuilder()

        self.backend.reset_index()

    def test_start_creates_index(self):
        # First, make sure the index is deleted
        try:
            self.es.indices.delete(self.backend.index_name)
        except self.NotFoundError:
            pass

        self.assertFalse(self.es.indices.exists(self.backend.index_name))

        # Run start
        self.rebuilder.start()

        # Check the index exists
        self.assertTrue(self.es.indices.exists(self.backend.index_name))

    def test_start_deletes_existing_index(self):
        # Put an alias into the index so we can check it was deleted
        self.es.indices.put_alias(name='this_index_should_be_deleted', index=self.backend.index_name)
        self.assertTrue(
            self.es.indices.exists_alias(name='this_index_should_be_deleted', index=self.backend.index_name)
        )

        # Run start
        self.rebuilder.start()

        # The alias should be gone (proving the index was deleted and recreated)
        self.assertFalse(
            self.es.indices.exists_alias(name='this_index_should_be_deleted', index=self.backend.index_name)
        )


@unittest.skipUnless(os.environ.get('ELASTICSEARCH2_URL', False), "ELASTICSEARCH2_URL not set")
class TestAtomicRebuilder(TestCase):
    def setUp(self):
        self.backend = get_search_backend('elasticsearch2')
        self.backend.rebuilder_class = self.backend.atomic_rebuilder_class
        self.es = self.backend.es
        self.rebuilder = self.backend.get_rebuilder()

        self.backend.reset_index()

    def test_start_creates_new_index(self):
        # Rebuilder should make up a new index name that doesn't currently exist
        self.assertFalse(self.es.indices.exists(self.rebuilder.index.name))

        # Run start
        self.rebuilder.start()

        # Check the index exists
        self.assertTrue(self.es.indices.exists(self.rebuilder.index.name))

    def test_start_doesnt_delete_current_index(self):
        # Get current index name
        current_index_name = list(self.es.indices.get_alias(name=self.rebuilder.alias.name).keys())[0]

        # Run start
        self.rebuilder.start()

        # The index should still exist
        self.assertTrue(self.es.indices.exists(current_index_name))

        # And the alias should still point to it
        self.assertTrue(self.es.indices.exists_alias(name=self.rebuilder.alias.name, index=current_index_name))

    def test_finish_updates_alias(self):
        # Run start
        self.rebuilder.start()

        # Check that the alias doesn't point to new index
        self.assertFalse(
            self.es.indices.exists_alias(name=self.rebuilder.alias.name, index=self.rebuilder.index.name)
        )

        # Run finish
        self.rebuilder.finish()

        # Check that the alias now points to the new index
        self.assertTrue(self.es.indices.exists_alias(name=self.rebuilder.alias.name, index=self.rebuilder.index.name))

    def test_finish_deletes_old_index(self):
        # Get current index name
        current_index_name = list(self.es.indices.get_alias(name=self.rebuilder.alias.name).keys())[0]

        # Run start
        self.rebuilder.start()

        # Index should still exist
        self.assertTrue(self.es.indices.exists(current_index_name))

        # Run finish
        self.rebuilder.finish()

        # Index should be gone
        self.assertFalse(self.es.indices.exists(current_index_name))
