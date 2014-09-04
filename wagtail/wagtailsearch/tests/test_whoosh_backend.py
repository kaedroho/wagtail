from wagtail.tests.utils import unittest
import datetime
import json

from django.test import TestCase
from django.db.models import Q

from wagtail.tests import models
from wagtail.wagtailsearch.backends.whoosh import WhooshMapping
from .test_backends import BackendTests


class TestWhooshBackend(BackendTests, TestCase):
    backend_path = 'wagtail.wagtailsearch.backends.whoosh.WhooshSearch'

    def test_partial_search(self):
        # Reset the index
        self.backend.reset_index()
        self.backend.add_type(models.SearchTest)
        self.backend.add_type(models.SearchTestChild)

        # Add some test data
        obj = models.SearchTest()
        obj.title = "HelloWorld"
        obj.live = True
        obj.save()
        self.backend.add(obj)

        # Refresh the index
        self.backend.refresh_index()

        # Search and check
        results = self.backend.search("HelloW", models.SearchTest.objects.all())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, obj.id)

    def test_child_partial_search(self):
        # Reset the index
        self.backend.reset_index()
        self.backend.add_type(models.SearchTest)
        self.backend.add_type(models.SearchTestChild)

        obj = models.SearchTestChild()
        obj.title = "WorldHello"
        obj.subtitle = "HelloWorld"
        obj.live = True
        obj.save()
        self.backend.add(obj)

        # Refresh the index
        self.backend.refresh_index()

        # Search and check
        results = self.backend.search("HelloW", models.SearchTest.objects.all())

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, obj.id)


class TestWhooshSchema(TestCase):
    def setUp(self):
        # Create Whoosh mapping
        self.whoosh_mapping = WhooshMapping(models.SearchTest)

        # Create an object
        self.obj = models.SearchTest(title="Hello")
        self.obj.save()

    def test_get_document_type(self):
        self.assertEqual(self.whoosh_mapping.get_document_type(), 'tests_searchtest')

    def test_get_document_id(self):
        self.assertEqual(self.whoosh_mapping.get_document_id(self.obj), 'tests_searchtest:' + str(self.obj.pk))

    def test_get_document(self):
        # Get document
        document = self.whoosh_mapping.get_document(self.obj)

        # Check


class TestWhooshSchemaInheritance(TestCase):
    def setUp(self):
        # Create Whoosh mapping
        self.whoosh_mapping = WhooshMapping(models.SearchTestChild)

        # Create an object
        self.obj = models.SearchTestChild(title="Hello", subtitle="World")
        self.obj.save()

    def test_get_document_type(self):
        self.assertEqual(self.whoosh_mapping.get_document_type(), 'tests_searchtest_tests_searchtestchild')

    def test_get_document_id(self):
        # This must be tests_searchtest instead of 'tests_searchtest_tests_searchtestchild'
        # as it uses the contents base content type name.
        # This prevents the same object being accidentally indexed twice.
        self.assertEqual(self.whoosh_mapping.get_document_id(self.obj), 'tests_searchtest:' + str(self.obj.pk))

    def test_get_document(self):
        # Build document
        document = self.whoosh_mapping.get_document(self.obj)

        # Check
