from django.test import TestCase
from django.utils import timezone
import datetime

from wagtail.tests.utils import unittest
from wagtail.wagtaileditorspicks.query import Query


class TestQueryHitCounter(TestCase):
    def test_no_hits(self):
        self.assertEqual(Query.get("Hello").hits, 0)

    def test_hit(self):
        # Add a hit
        Query.get("Hello").add_hit()

        # Test
        self.assertEqual(Query.get("Hello").hits, 1)

    def test_10_hits(self):
        # Add 10 hits
        for i in range(10):
            Query.get("Hello").add_hit()

        # Test
        self.assertEqual(Query.get("Hello").hits, 10)

    def test_old_hits(self):
        """
        Hits older than 7 days shouldn't be counted
        """
        # Add a hit 2 weeks ago
        Query.get("Old query").add_hit(date=datetime.date(2014, 05, 10))

        # Test
        self.assertEqual(Query.get("Hello").get_hits(date=datetime.date(2014, 05, 24)), 0)


class TestQueryPopularity(TestCase):
    def test_query_popularity(self):
        # Add 3 hits to unpopular query
        for i in range(3):
            Query.get("unpopular query").add_hit()

        # Add 10 hits to popular query
        for i in range(10):
            Query.get("popular query").add_hit()

        # Get most popular queries
        popular_queries = Query.get_most_popular()

        # Check list
        self.assertEqual(popular_queries.count(), 2)
        self.assertEqual(popular_queries[0]['query_string'], "popular query")
        self.assertEqual(popular_queries[1]['query_string'], "unpopular query")

        # Add 5 hits to little popular query
        for i in range(5):
            Query.get("little popular query").add_hit()

        # Check list again, little popular query should be in the middle
        self.assertEqual(popular_queries.count(), 3)
        self.assertEqual(popular_queries[0]['query_string'], "popular query")
        self.assertEqual(popular_queries[1]['query_string'], "little popular query")
        self.assertEqual(popular_queries[2]['query_string'], "unpopular query")

        # Unpopular query goes viral!
        for i in range(20):
            Query.get("unpopular query").add_hit()

        # Unpopular query should be most popular now
        self.assertEqual(popular_queries.count(), 3)
        self.assertEqual(popular_queries[0]['query_string'], "unpopular query")
        self.assertEqual(popular_queries[1]['query_string'], "popular query")
        self.assertEqual(popular_queries[2]['query_string'], "little popular query")
