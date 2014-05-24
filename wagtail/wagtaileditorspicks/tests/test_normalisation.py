from django.test import TestCase
from wagtail.tests.utils import unittest

from wagtail.wagtaileditorspicks.utils import normalise_query_string


class TestQueryStringNormalisation(TestCase):
    def test_lowercase(self):
        """
        Must be lowercase
        """
        self.assertEqual(
            normalise_query_string("Hello World"),
            "hello world",
        )

    def test_punctuation_removal(self):
        """
        All punctuation must be removed
        """
        self.assertEqual(
            normalise_query_string("He_l-l$o. World!"),
            "hello world",
        )

    def test_space_removal(self):
        """
        All multi spaces must be replaced with a single space
        All leading and trailing spaces must be removed
        """
        self.assertEqual(
            normalise_query_string(" hello   world  "),
            "hello world",
        )
