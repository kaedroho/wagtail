from django.test import TestCase
from django.core import management
from wagtail.tests.utils import login


class TestQueryChooserView(TestCase):
    def setUp(self):
        login(self.client)

    def get(self, params={}):
        return self.client.get('/admin/editorspicks/queries/chooser/', params)

    def test_status_code(self):
        self.assertEqual(self.get().status_code, 200)

    def test_search(self):
        response = self.get({'q': "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query_string'], "Hello")

    def test_pagination(self):
        pages = ['0', '1', '-1', '9999', 'Not a page']
        for page in pages:
            response = self.get({'p': page})
            self.assertEqual(response.status_code, 200)
