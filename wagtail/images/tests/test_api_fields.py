import datetime

from django.test import TestCase

from wagtail.core.models import Page
from wagtail.images.api.fields import ImageRenditionAPIField, ImageRenditionField
from wagtail.tests.testapp.models import EventPage

from .utils import Image, get_test_image_file


class TestImageRenditionField(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

    def test_api_representation(self):
        representation = ImageRenditionField('width-400').to_representation(self.image)

        rendition = self.image.get_rendition('width-400')
        self.assertEqual(set(representation.keys()), {'url', 'width', 'height', 'alt'})
        self.assertEqual(representation['url'], rendition.url)
        self.assertEqual(representation['width'], rendition.width)
        self.assertEqual(representation['height'], rendition.height)
        self.assertEqual(representation['alt'], rendition.alt)


class TestImageRenditionAPIField(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        home_page = Page.objects.get(depth=2)
        self.page = home_page.add_child(instance=EventPage(
            title="Event page",
            slug="event-page",
            date_from=datetime.date(2021, 6, 28),
            date_to=datetime.date(2021, 6, 28),
            audience="public",
            location="Online",
            cost="Free",
            feed_image=self.image
        ))

    def test_api_representation(self):
        representation = ImageRenditionAPIField('feed_image', 'width-400').serializer.to_representation(self.feed_image)

        rendition = self.image.get_rendition('width-400')
        self.assertEqual(set(representation.keys()), {'url', 'width', 'height', 'alt'})
        self.assertEqual(representation['url'], rendition.url)
        self.assertEqual(representation['width'], rendition.width)
        self.assertEqual(representation['height'], rendition.height)
        self.assertEqual(representation['alt'], rendition.alt)

    def test_prefetches_renditions(self):
        queryset = ImageRenditionAPIField('feed_image', 'width-400').select_on_queryset(EventPage.objects.all())

        self.assertEqual(len(queryset._prefetch_related_lookups), 1)
        prefetch = queryset._prefetch_related_lookups[0]
        self.assertEqual(prefetch.prefetch_through, 'feed_image__renditions')
        self.assertEqual(prefetch.to_attr, 'prefetched_renditions')
