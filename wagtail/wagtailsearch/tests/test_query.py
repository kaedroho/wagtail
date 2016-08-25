from __future__ import absolute_import, unicode_literals

import datetime

from django.db.models import Q
from django.test import TestCase

from wagtail.tests.search import models
from wagtail.wagtailsearch import query
from wagtail.wagtailsearch.utils import convert_where_node_to_query


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


class TestConvertWhereNodeToQuery(TestCase):
    def test_simple(self):
        qs = models.SearchTest.objects.all()

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsNone(q)

    def test_exact_lookup(self):
        qs = models.SearchTest.objects.filter(title="foo")

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.TermQuery)
        self.assertEqual(q.field, 'title')
        self.assertEqual(q.value, 'foo')

    def test_startswith_lookup(self):
        qs = models.SearchTest.objects.filter(title__startswith="foo")

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.PrefixQuery)
        self.assertEqual(q.field, 'title')
        self.assertEqual(q.prefix, 'foo')

    def test_gt_lookup(self):
        qs = models.SearchTest.objects.filter(published_date__gt=datetime.date(2016, 8, 28))

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.RangeQuery)
        self.assertEqual(q.from_, datetime.date(2016, 8, 28))
        self.assertEqual(q.from_included, False)
        self.assertIsNone(q.to)

    def test_gte_lookup(self):
        qs = models.SearchTest.objects.filter(published_date__gte=datetime.date(2016, 8, 28))

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.RangeQuery)
        self.assertEqual(q.from_, datetime.date(2016, 8, 28))
        self.assertEqual(q.from_included, True)
        self.assertIsNone(q.to)

    def test_lt_lookup(self):
        qs = models.SearchTest.objects.filter(published_date__lt=datetime.date(2016, 8, 28))

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.RangeQuery)
        self.assertEqual(q.to, datetime.date(2016, 8, 28))
        self.assertEqual(q.to_included, False)
        self.assertIsNone(q.from_)

    def test_lte_lookup(self):
        qs = models.SearchTest.objects.filter(published_date__lte=datetime.date(2016, 8, 28))

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.RangeQuery)
        self.assertEqual(q.to, datetime.date(2016, 8, 28))
        self.assertEqual(q.to_included, True)
        self.assertIsNone(q.from_)

    def test_range_lookup(self):
        qs = models.SearchTest.objects.filter(published_date__range=(datetime.date(2016, 8, 19), datetime.date(2016, 8, 28)))

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.RangeQuery)
        self.assertEqual(q.from_, datetime.date(2016, 8, 19))
        self.assertEqual(q.from_included, True)
        self.assertEqual(q.to, datetime.date(2016, 8, 28))
        self.assertEqual(q.to_included, True)

    def test_in_lookup(self):
        qs = models.SearchTest.objects.filter(title__in=['foo', 'bar', 'baz'])

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.DisjunctionQuery)
        for subquery in q.subqueries:
            self.assertIsInstance(subquery, query.TermQuery)
            self.assertEqual(subquery.field, 'title')

        self.assertEqual(q.subqueries[0].value, 'foo')
        self.assertEqual(q.subqueries[1].value, 'bar')
        self.assertEqual(q.subqueries[2].value, 'baz')

    def test_combination_and(self):
        qs1 = models.SearchTest.objects.filter(title='foo')
        qs2 = models.SearchTest.objects.filter(title='bar')
        qs = qs1 & qs2

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.ConjunctionQuery)
        for subquery in q.subqueries:
            self.assertIsInstance(subquery, query.TermQuery)
            self.assertEqual(subquery.field, 'title')

        self.assertEqual(q.subqueries[0].value, 'foo')
        self.assertEqual(q.subqueries[1].value, 'bar')

    def test_combination_or(self):
        qs1 = models.SearchTest.objects.filter(title='foo')
        qs2 = models.SearchTest.objects.filter(title='bar')
        qs = qs1 | qs2

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.DisjunctionQuery)
        for subquery in q.subqueries:
            self.assertIsInstance(subquery, query.TermQuery)
            self.assertEqual(subquery.field, 'title')

        self.assertEqual(q.subqueries[0].value, 'foo')
        self.assertEqual(q.subqueries[1].value, 'bar')

    def test_combination_same_filter(self):
        qs = models.SearchTest.objects.filter(title='foo', live=True)

        q = convert_where_node_to_query(qs.query.where)

        subqueries_dict = {}
        self.assertIsInstance(q, query.ConjunctionQuery)
        for subquery in q.subqueries:
            self.assertIsInstance(subquery, query.TermQuery)
            subqueries_dict[subquery.field] = subquery.value

        self.assertEqual(subqueries_dict['title'], 'foo')
        self.assertEqual(subqueries_dict['live'], True)

    def test_combination_q_object(self):
        qs = models.SearchTest.objects.filter(Q(title='foo') | Q(live=True))

        q = convert_where_node_to_query(qs.query.where)

        subqueries_dict = {}
        self.assertIsInstance(q, query.DisjunctionQuery)
        for subquery in q.subqueries:
            self.assertIsInstance(subquery, query.TermQuery)
            subqueries_dict[subquery.field] = subquery.value

        self.assertEqual(subqueries_dict['title'], 'foo')
        self.assertEqual(subqueries_dict['live'], True)

    def test_negation(self):
        qs = models.SearchTest.objects.exclude(title="foo")

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.FilterQuery)
        self.assertIsInstance(q.query, query.MatchAllQuery)

        self.assertIsInstance(q.exclude, query.TermQuery)
        self.assertEqual(q.exclude.field, 'title')
        self.assertEqual(q.exclude.value, 'foo')

    def test_negation_q_object(self):
        qs = models.SearchTest.objects.filter(~Q(title='foo'))

        q = convert_where_node_to_query(qs.query.where)

        self.assertIsInstance(q, query.FilterQuery)
        self.assertIsInstance(q.query, query.MatchAllQuery)

        self.assertIsInstance(q.exclude, query.TermQuery)
        self.assertEqual(q.exclude.field, 'title')
        self.assertEqual(q.exclude.value, 'foo')
