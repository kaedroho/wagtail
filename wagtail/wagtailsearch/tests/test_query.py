from __future__ import absolute_import, unicode_literals

from django.test import TestCase

from wagtail.wagtailsearch import query


class TestCombinators(TestCase):
    def test_and(self):
        query_a = query.MatchQuery("foo")
        query_b = query.MatchQuery("bar")

        combined = query_a & query_b

        self.assertIsInstance(combined, query.ConjunctionQuery)
        self.assertListEqual(combined.subqueries, [query_a, query_b])

    def test_or(self):
        query_a = query.MatchQuery("foo")
        query_b = query.MatchQuery("bar")

        combined = query_a | query_b

        self.assertIsInstance(combined, query.DisjunctionQuery)
        self.assertListEqual(combined.subqueries, [query_a, query_b])

    def test_invert(self):
        query_a = query.MatchQuery("foo")

        inverted = ~query_a

        self.assertIsInstance(inverted, query.FilterQuery)
        self.assertIsInstance(inverted.query, query.MatchAllQuery)
        self.assertEqual(inverted.exclude, query_a)
