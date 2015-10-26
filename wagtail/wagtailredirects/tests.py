# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import random
import io

import unicodecsv

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from wagtail.tests.utils import WagtailTestUtils
from wagtail.wagtailredirects import models
from wagtail.wagtailredirects.redirect_csv_import import import_redirect_csv, InvalidRedirectCSVException


class TestRedirects(TestCase):
    def test_path_normalisation(self):
        # Shortcut to normalise function (to keep things tidy)
        normalise_path = models.Redirect.normalise_path

        # Create a path
        path = normalise_path('/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2')

        # Test against equivalant paths
        self.assertEqual(path, normalise_path('/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # The exact same URL
        self.assertEqual(path, normalise_path('http://mywebsite.com:8000/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # Scheme, hostname and port ignored
        self.assertEqual(path, normalise_path('Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # Leading slash can be omitted
        self.assertEqual(path, normalise_path('Hello/world.html/;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # Trailing slashes are ignored
        self.assertEqual(path, normalise_path('/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2#cool')) # Fragments are ignored
        self.assertEqual(path, normalise_path('/Hello/world.html;fizz=three;buzz=five?Baz=quux2&foo=Bar')) # Order of query string parameters is ignored
        self.assertEqual(path, normalise_path('/Hello/world.html;buzz=five;fizz=three?foo=Bar&Baz=quux2')) # Order of parameters is ignored
        self.assertEqual(path, normalise_path('  /Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # Leading whitespace
        self.assertEqual(path, normalise_path('/Hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2  ')) # Trailing whitespace

        # Test against different paths
        self.assertNotEqual(path, normalise_path('/hello/world.html;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # 'hello' is lowercase
        self.assertNotEqual(path, normalise_path('/Hello/world;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # No '.html'
        self.assertNotEqual(path, normalise_path('/Hello/world.html;fizz=three;buzz=five?foo=bar&Baz=Quux2')) # Query string parameter value has wrong case
        self.assertNotEqual(path, normalise_path('/Hello/world.html;fizz=three;buzz=five?foo=Bar&baz=quux2')) # Query string parameter name has wrong case
        self.assertNotEqual(path, normalise_path('/Hello/world.html;fizz=three;buzz=Five?foo=Bar&Baz=quux2')) # Parameter value has wrong case
        self.assertNotEqual(path, normalise_path('/Hello/world.html;Fizz=three;buzz=five?foo=Bar&Baz=quux2')) # Parameter name has wrong case
        self.assertNotEqual(path, normalise_path('/Hello/world.html?foo=Bar&Baz=quux2')) # Missing params
        self.assertNotEqual(path, normalise_path('/Hello/WORLD.html;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # 'WORLD' is uppercase
        self.assertNotEqual(path, normalise_path('/Hello/world.htm;fizz=three;buzz=five?foo=Bar&Baz=quux2')) # '.htm' is not the same as '.html'

        # Normalise some rubbish to make sure it doesn't crash
        normalise_path('This is not a URL')
        normalise_path('//////hello/world')
        normalise_path('!#@%$*')
        normalise_path('C:\\Program Files (x86)\\Some random program\\file.txt')

    def test_basic_redirect(self):
        # Get a client
        c = Client()

        # Create a redirect
        redirect = models.Redirect(old_path='/redirectme', redirect_link='/redirectto')
        redirect.save()

        # Navigate to it
        r = c.get('/redirectme/')

        # Check that we were redirected
        self.assertEqual(r.status_code, 301)
        self.assertTrue(r.has_header('Location'))

    def test_temporary_redirect(self):
        # Get a client
        c = Client()

        # Create a redirect
        redirect = models.Redirect(old_path='/redirectme', redirect_link='/redirectto', is_permanent=False)
        redirect.save()

        # Navigate to it
        r = c.get('/redirectme/')

        # Check that we were redirected temporarily
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.has_header('Location'))

    def test_redirect_stripping_query_string(self):
        # Get a client
        c = Client()

        # Create a redirect which includes a query string
        redirect_with_query_string = models.Redirect(old_path='/redirectme?foo=Bar', redirect_link='/with-query-string-only')
        redirect_with_query_string.save()

        # ... and another redirect without the query string
        redirect_without_query_string = models.Redirect(old_path='/redirectme', redirect_link='/without-query-string')
        redirect_without_query_string.save()

        # Navigate to the redirect with the query string
        r_matching_qs = c.get('/redirectme/?foo=Bar')
        self.assertEqual(r_matching_qs.status_code, 301)
        self.assertTrue(r_matching_qs.has_header('Location'))
        self.assertEqual(r_matching_qs['Location'][-23:], '/with-query-string-only')

        # Navigate to the redirect with a different query string
        # This should strip out the query string and match redirect_without_query_string
        r_no_qs = c.get('/redirectme/?utm_source=irrelevant')
        self.assertEqual(r_no_qs.status_code, 301)
        self.assertTrue(r_no_qs.has_header('Location'))
        self.assertEqual(r_no_qs['Location'][-21:], '/without-query-string')

class TestRedirectsIndexView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse('wagtailredirects:index'), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailredirects/index.html')

    def test_search(self):
        response = self.get({'q': "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['query_string'], "Hello")

    def test_pagination(self):
        pages = ['0', '1', '-1', '9999', 'Not a page']
        for page in pages:
            response = self.get({'p': page})
            self.assertEqual(response.status_code, 200)


class TestRedirectsAddView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse('wagtailredirects:add'), params)

    def post(self, post_data={}):
        return self.client.post(reverse('wagtailredirects:add'), post_data)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailredirects/add.html')

    def test_add(self):
        response = self.post({
            'old_path': '/test',
            'is_permanent': 'on',
            'redirect_link': 'http://www.test.com/',
        })

        # Should redirect back to index
        self.assertRedirects(response, reverse('wagtailredirects:index'))

        # Check that the redirect was created
        redirects = models.Redirect.objects.filter(old_path='/test')
        self.assertEqual(redirects.count(), 1)
        self.assertEqual(redirects.first().redirect_link, 'http://www.test.com/')
        self.assertEqual(redirects.first().site, None)

    def test_add_validation_error(self):
        response = self.post({
            'old_path': '',
            'is_permanent': 'on',
            'redirect_link': 'http://www.test.com/',
        })

        # Should not redirect to index
        self.assertEqual(response.status_code, 200)


class TestRedirectsEditView(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create a redirect to edit
        self.redirect = models.Redirect(old_path='/test', redirect_link='http://www.test.com/')
        self.redirect.save()

        # Login
        self.login()

    def get(self, params={}, redirect_id=None):
        return self.client.get(reverse('wagtailredirects:edit', args=(redirect_id or self.redirect.id, )), params)

    def post(self, post_data={}, redirect_id=None):
        return self.client.post(reverse('wagtailredirects:edit', args=(redirect_id or self.redirect.id, )), post_data)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailredirects/edit.html')

    def test_nonexistant_redirect(self):
        self.assertEqual(self.get(redirect_id=100000).status_code, 404)

    def test_edit(self):
        response = self.post({
            'old_path': '/test',
            'is_permanent': 'on',
            'redirect_link': 'http://www.test.com/ive-been-edited',
        })

        # Should redirect back to index
        self.assertRedirects(response, reverse('wagtailredirects:index'))

        # Check that the redirect was edited
        redirects = models.Redirect.objects.filter(old_path='/test')
        self.assertEqual(redirects.count(), 1)
        self.assertEqual(redirects.first().redirect_link, 'http://www.test.com/ive-been-edited')

    def test_edit_validation_error(self):
        response = self.post({
            'old_path': '',
            'is_permanent': 'on',
            'redirect_link': 'http://www.test.com/ive-been-edited',
        })

        # Should not redirect to index
        self.assertEqual(response.status_code, 200)


class TestRedirectsDeleteView(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create a redirect to edit
        self.redirect = models.Redirect(old_path='/test', redirect_link='http://www.test.com/')
        self.redirect.save()

        # Login
        self.login()

    def get(self, params={}, redirect_id=None):
        return self.client.get(reverse('wagtailredirects:delete', args=(redirect_id or self.redirect.id, )), params)

    def post(self, post_data={}, redirect_id=None):
        return self.client.post(reverse('wagtailredirects:delete', args=(redirect_id or self.redirect.id, )), post_data)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailredirects/confirm_delete.html')

    def test_nonexistant_redirect(self):
        self.assertEqual(self.get(redirect_id=100000).status_code, 404)

    def test_delete(self):
        response = self.post({
            'hello': 'world'
        })

        # Should redirect back to index
        self.assertRedirects(response, reverse('wagtailredirects:index'))

        # Check that the redirect was deleted
        redirects = models.Redirect.objects.filter(old_path='/test')
        self.assertEqual(redirects.count(), 0)


class TestRedirectCSVImport(TestCase):
    def make_csv(self, data, encoding='UTF-8', line_ending='\r\n'):
        sio = io.StringIO()
        writer = unicodecsv.writer(sio, lineterminator=line_ending)
        writer.writerows(data)

        # Encode to a BytesIO to make it like a real file
        return io.BytesIO(sio.getvalue().encode(encoding))

    def test_redirect_to_external(self):
        f = self.make_csv([
            ('/myredirect', 'http://example.com'),
        ])

        import_redirect_csv(f)

    def test_redirect_to_internal_path(self):
        f = self.make_csv([
            ('/myredirect', '/test'),
        ])

        import_redirect_csv(f)

    def test_redirect_to_page(self):
        # TODO: Make a page
        f = self.make_csv([
            ('/myredirect', '/testpage'),
        ])

        import_redirect_csv(f)

    @unittest.expectedFailure
    def test_ignores_header(self):
        f = self.make_csv([
            ('redirect from', 'redirect to'),
            ('/myredirect', 'http://example.com'),
        ])

        # Shouldn't raise exception
        import_redirect_csv(f)

    def test_strips_whitespace(self):
        f = self.make_csv([
            ('   /myredirect   ', '   http://example.com '),
        ])

        import_redirect_csv(f)

    def test_detects_preexisting_redirect(self):
        # MAKE A REDIRECT

        f = self.make_csv([
            ('/myredirect', 'http://example.com'),
        ])

        import_redirect_csv(f)

    def test_handles_unicode_path(self):
        f = self.make_csv([
            ('/转向', 'http://example.com'),
        ])

        import_redirect_csv(f)

    def test_handles_unicode_domain(self):
        f = self.make_csv([
            ('/myredirect', 'http://转向.com'),
        ])

        import_redirect_csv(f)

    def test_handles_stupid_line_endings(self):
        f = self.make_csv([
            ('/myredirect', 'http://example.com'),
        ], line_ending='\r')

        import_redirect_csv(f)

    def test_handles_extra_blank_row(self):
        f = self.make_csv([
            ('/myredirect', 'http://example.com'),
            ('', ''),
        ])

        import_redirect_csv(f)


    # Failure tests

    def assertNoRedirects(self):
        # In the event of a failed import, no redirects should be imported
        self.assertFalse(models.Redirect.objects.exists(), "The import failed but some redirects were imported")

    def test_extra_column(self):
        f = self.make_csv([
            ('/myredirect', 'http://example.com', 'extra column'),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "CSV file has 3 columns. It should have 2.")
        self.assertNoRedirects()

    def test_missing_columns(self):
        f = self.make_csv([
            ('/myredirect', ),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "CSV file has 1 columns. It should have 2.")
        self.assertNoRedirects()

    def test_missing_path(self):
        f = self.make_csv([
            ('', 'http://example.com'),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "[ROW 1] From path must not be blank.")
        self.assertNoRedirects()

    def test_missing_url(self):
        f = self.make_csv([
            ('/myredirect', ''),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "[ROW 1] URL must not be blank.")
        self.assertNoRedirects()

    def test_no_forward_slash_in_path(self):
        f = self.make_csv([
            ('path', 'url'),  # Allow in first row so headers can be handled correctly
            ('myredirect', 'http://example.com'),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "[ROW 1] From path must begin with a '/'.")
        self.assertNoRedirects()

    def test_url_in_path(self):
        f = self.make_csv([
            ('http://myredirect', 'http://example.com'),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "[ROW 1] From path must begin with a '/'.")
        self.assertNoRedirects()

    def test_no_forward_slash_or_scheme_in_url(self):
        f = self.make_csv([
            ('/myredirect', 'example'),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "[ROW 1] Invalid URL.")
        self.assertNoRedirects()

    def test_bad_scheme_in_url(self):
        f = self.make_csv([
            ('/myredirect', 'gopher://example.com'),
        ])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "[ROW 1] Unknown scheme used in URL.")
        self.assertNoRedirects()

    def test_bad_encoding(self):
        f = self.make_csv([
            ('/myredirect', 'http://example.com'),
        ], encoding='UTF-16')

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "Unable to read file. Is it a valid CSV file with UTF-8 encoding?")
        self.assertNoRedirects()

    @unittest.expectedFailure
    def test_junk(self):
        f = BytesIO([random.randint(0, 255) for byte in range(100)])

        with self.assertRaises(InvalidRedirectCSVException) as e:
            import_redirect_csv(f)

        self.assertEqual(str(e.exception), "Unable to read file. Is it a valid CSV file with UTF-8 encoding?")
        self.assertNoRedirects()
