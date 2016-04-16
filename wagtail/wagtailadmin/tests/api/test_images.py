import json

from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from wagtail.api.v2.tests.test_images import TestImageDetail, TestImageListing
from wagtail.wagtailimages.models import get_image_model
from wagtail.wagtailimages.tests.utils import get_test_image_file

from .utils import AdminAPITestCase


class TestAdminImageListing(AdminAPITestCase, TestImageListing):
    fixtures = ['demosite.json']

    def get_response(self, **params):
        return self.client.get(reverse('wagtailadmin_api_v1:images:listing'), params)

    def get_image_id_list(self, content):
        return [image['id'] for image in content['items']]


    # BASIC TESTS

    def test_basic(self):
        response = self.get_response()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-type'], 'application/json')

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode('UTF-8'))

        # Check that the meta section is there
        self.assertIn('meta', content)
        self.assertIsInstance(content['meta'], dict)

        # Check that the total count is there and correct
        self.assertIn('total_count', content['meta'])
        self.assertIsInstance(content['meta']['total_count'], int)
        self.assertEqual(content['meta']['total_count'], get_image_model().objects.count())

        # Check that the items section is there
        self.assertIn('items', content)
        self.assertIsInstance(content['items'], list)

        # Check that each image has a meta section with type, detail_url and tags attributes
        for image in content['items']:
            self.assertIn('meta', image)
            self.assertIsInstance(image['meta'], dict)
            self.assertEqual(set(image['meta'].keys()), {'type', 'detail_url', 'tags'})  # ADMINAPI CHANGE

            # Type should always be wagtailimages.Image
            self.assertEqual(image['meta']['type'], 'wagtailimages.Image')

            # Check detail url
            self.assertEqual(image['meta']['detail_url'], 'http://localhost/admin/api/v2beta/images/%d/' % image['id'])


    #  FIELDS

    def test_fields_default(self):  # ADMINAPI CHANGE
        response = self.get_response()
        content = json.loads(response.content.decode('UTF-8'))

        for image in content['items']:
            self.assertEqual(set(image.keys()), {'id', 'meta', 'title', 'width', 'height', 'thumbnail'})
            self.assertEqual(set(image['meta'].keys()), {'type', 'detail_url', 'tags'})


class TestAdminImageDetail(AdminAPITestCase, TestImageDetail):
    fixtures = ['demosite.json']

    def get_response(self, image_id, **params):
        return self.client.get(reverse('wagtailadmin_api_v1:images:detail', args=(image_id, )), params)


    def test_basic(self):
        response = self.get_response(5)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-type'], 'application/json')

        # Will crash if the JSON is invalid
        content = json.loads(response.content.decode('UTF-8'))

        # Check the id field
        self.assertIn('id', content)
        self.assertEqual(content['id'], 5)

        # Check that the meta section is there
        self.assertIn('meta', content)
        self.assertIsInstance(content['meta'], dict)

        # Check the meta type
        self.assertIn('type', content['meta'])
        self.assertEqual(content['meta']['type'], 'wagtailimages.Image')

        # Check the meta detail_url
        self.assertIn('detail_url', content['meta'])
        self.assertEqual(content['meta']['detail_url'], 'http://localhost/admin/api/v2beta/images/5/')

        # Check the thumbnail
        # ADMINAPI CHANGE
        # Note: This is None because the source image doesn't exist
        #       See test_thumbnail below for working example
        self.assertIn('thumbnail', content)
        self.assertEqual(content['thumbnail'], {'error': 'SourceImageIOError'})

        # Check the title field
        self.assertIn('title', content)
        self.assertEqual(content['title'], "James Joyce")

        # Check the width and height fields
        self.assertIn('width', content)
        self.assertIn('height', content)
        self.assertEqual(content['width'], 500)
        self.assertEqual(content['height'], 392)

        # Check the tags field
        self.assertIn('tags', content['meta'])
        self.assertEqual(content['meta']['tags'], [])

    def test_thumbnail(self):  # ADMINAPI CHANGE
        # Add a new image with source file
        image = get_image_model().objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        response = self.get_response(image.id)
        content = json.loads(response.content.decode('UTF-8'))

        self.assertIn('thumbnail', content)
        self.assertEqual(content['thumbnail'], {
            'url': '/media/images/test.max-165x165.png',
            'width': 165,
            'height': 123
        })

        # Check that source_image_error didn't appear
        self.assertNotIn('source_image_error', content['meta'])
